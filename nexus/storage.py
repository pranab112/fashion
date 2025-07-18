from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.core.files.base import ContentFile
from django.utils.text import slugify
from typing import Optional, Dict, Any, BinaryIO, Union
import os
import boto3
import logging
from PIL import Image
from io import BytesIO
import magic
import hashlib
from datetime import datetime
from pathlib import Path
from .monitoring import Monitoring

logger = logging.getLogger(__name__)

class StorageService:
    """Service class for handling file storage operations."""

    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    IMAGE_SIZES = {
        'thumbnail': (150, 150),
        'small': (300, 300),
        'medium': (600, 600),
        'large': (1200, 1200),
    }

    @classmethod
    def get_storage(cls) -> Storage:
        """Get appropriate storage backend based on settings."""
        if settings.USE_S3:
            return S3Storage()
        return LocalStorage()

    @classmethod
    @Monitoring.monitor_performance
    def save_file(
        cls,
        file: BinaryIO,
        path: str,
        filename: Optional[str] = None,
        public: bool = False
    ) -> Dict[str, str]:
        """
        Save file to storage.
        
        Args:
            file: File object
            path: Storage path
            filename: Optional filename (will be sanitized)
            public: Whether file should be publicly accessible
        
        Returns:
            Dict containing file URL and metadata
        """
        try:
            # Validate file
            cls._validate_file(file)

            # Generate safe filename
            if filename:
                filename = cls._sanitize_filename(filename)
            else:
                filename = cls._generate_filename(file)

            # Get full path
            full_path = os.path.join(path, filename)

            # Save file
            storage = cls.get_storage()
            saved_path = storage.save(full_path, file)

            # Generate URLs
            url = storage.url(saved_path)
            
            return {
                'url': url,
                'path': saved_path,
                'filename': filename,
                'size': file.size,
                'mime_type': magic.from_buffer(file.read(1024), mime=True),
            }

        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            raise

    @classmethod
    def save_image(
        cls,
        image: BinaryIO,
        path: str,
        filename: Optional[str] = None,
        generate_sizes: bool = True
    ) -> Dict[str, Dict[str, str]]:
        """
        Save image with optional size variants.
        
        Args:
            image: Image file
            path: Storage path
            filename: Optional filename
            generate_sizes: Whether to generate size variants
        """
        try:
            # Validate image
            cls._validate_image(image)

            # Process original image
            img = Image.open(image)
            
            # Convert to RGB if necessary
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')

            # Generate safe filename
            if filename:
                filename = cls._sanitize_filename(filename)
            else:
                filename = cls._generate_filename(image)

            # Save original
            storage = cls.get_storage()
            urls = {'original': cls.save_file(image, path, filename)}

            if generate_sizes:
                # Generate and save variants
                name, ext = os.path.splitext(filename)
                for size_name, dimensions in cls.IMAGE_SIZES.items():
                    size_filename = f"{name}_{size_name}{ext}"
                    resized = cls._resize_image(img, dimensions)
                    
                    # Convert to BytesIO
                    buffer = BytesIO()
                    resized.save(buffer, format=img.format or 'JPEG')
                    buffer.seek(0)
                    
                    urls[size_name] = cls.save_file(
                        buffer,
                        os.path.join(path, size_name),
                        size_filename
                    )

            return urls

        except Exception as e:
            logger.error(f"Image save error: {str(e)}")
            raise

    @classmethod
    def delete_file(cls, path: str) -> bool:
        """Delete file from storage."""
        try:
            storage = cls.get_storage()
            storage.delete(path)
            return True
        except Exception as e:
            logger.error(f"File delete error: {str(e)}")
            return False

    @classmethod
    def _validate_file(cls, file: BinaryIO) -> None:
        """Validate file size and type."""
        # Check file size
        if file.size > cls.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds {cls.MAX_FILE_SIZE} bytes")

        # Check file type
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Reset file pointer

        if not mime_type:
            raise ValueError("Could not determine file type")

        # Add more validation as needed
        if mime_type.startswith('image/'):
            cls._validate_image(file)

    @classmethod
    def _validate_image(cls, image: BinaryIO) -> None:
        """Validate image file."""
        try:
            img = Image.open(image)
            img.verify()
            image.seek(0)  # Reset file pointer

            # Check extension
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in cls.ALLOWED_IMAGE_EXTENSIONS:
                raise ValueError(f"Invalid image extension: {ext}")

            # Check dimensions
            if img.size[0] > 4096 or img.size[1] > 4096:
                raise ValueError("Image dimensions too large")

        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename."""
        # Get name and extension
        name, ext = os.path.splitext(filename)
        
        # Sanitize name
        name = slugify(name)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{name}_{timestamp}{ext.lower()}"

    @staticmethod
    def _generate_filename(file: BinaryIO) -> str:
        """Generate unique filename."""
        # Generate hash from file content
        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)  # Reset file pointer
        
        # Get extension
        ext = os.path.splitext(file.name)[1].lower()
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{file_hash}_{timestamp}{ext}"

    @staticmethod
    def _resize_image(img: Image.Image, size: tuple) -> Image.Image:
        """Resize image maintaining aspect ratio."""
        img.thumbnail(size, Image.LANCZOS)
        return img

class LocalStorage(FileSystemStorage):
    """Local file system storage backend."""

    def __init__(self):
        super().__init__(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL
        )

    def url(self, name: str) -> str:
        """Get URL for file."""
        return super().url(name)

class S3Storage(Storage):
    """Amazon S3 storage backend."""

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.cdn_domain = settings.AWS_S3_CUSTOM_DOMAIN

    def _save(self, name: str, content: BinaryIO) -> str:
        """Save file to S3."""
        try:
            self.client.upload_fileobj(
                content,
                self.bucket,
                name,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': magic.from_buffer(
                        content.read(1024),
                        mime=True
                    )
                }
            )
            return name
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise

    def _open(self, name: str, mode: str = 'rb') -> BinaryIO:
        """Get file from S3."""
        try:
            obj = self.client.get_object(
                Bucket=self.bucket,
                Key=name
            )
            return ContentFile(obj['Body'].read())
        except Exception as e:
            logger.error(f"S3 download error: {str(e)}")
            raise

    def delete(self, name: str) -> None:
        """Delete file from S3."""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=name
            )
        except Exception as e:
            logger.error(f"S3 delete error: {str(e)}")
            raise

    def exists(self, name: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=name
            )
            return True
        except:
            return False

    def url(self, name: str) -> str:
        """Get URL for file."""
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{name}"
        return f"https://{self.bucket}.s3.amazonaws.com/{name}"

    def size(self, name: str) -> int:
        """Get file size."""
        try:
            obj = self.client.head_object(
                Bucket=self.bucket,
                Key=name
            )
            return obj['ContentLength']
        except Exception as e:
            logger.error(f"S3 size check error: {str(e)}")
            raise

    def get_modified_time(self, name: str) -> datetime:
        """Get last modified time."""
        try:
            obj = self.client.head_object(
                Bucket=self.bucket,
                Key=name
            )
            return obj['LastModified']
        except Exception as e:
            logger.error(f"S3 modified time check error: {str(e)}")
            raise
