"""
Custom storage backends for the products app.
"""

import os
import hashlib
from typing import Any, Optional
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from storages.backends.s3boto3 import S3Boto3Storage

class ProductImageStorage(FileSystemStorage):
    """Custom storage for product images with optimized organization."""
    
    def __init__(self):
        """Initialize storage with product media location."""
        location = os.path.join(settings.MEDIA_ROOT, 'products')
        super().__init__(location=location)

    def get_valid_name(self, name: str) -> str:
        """
        Return a filename suitable for use with this storage.
        
        Args:
            name: Original filename
            
        Returns:
            str: Valid filename
        """
        # Clean the filename
        name = slugify(os.path.splitext(name)[0])
        ext = os.path.splitext(name)[1].lower()
        
        # Ensure valid image extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if ext not in valid_extensions:
            ext = '.jpg'
            
        return f"{name}{ext}"

    def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
        """
        Return a filename that's free on the target storage system.
        
        Args:
            name: Desired filename
            max_length: Maximum length for filename
            
        Returns:
            str: Available filename
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        
        # Generate unique filename
        count = 0
        while self.exists(name):
            count += 1
            name = os.path.join(
                dir_name,
                f"{file_root}_{count}{file_ext}"
            )
            
        return name

    def get_alternative_name(self, file_root: str, file_ext: str) -> str:
        """
        Return an alternative filename.
        
        Args:
            file_root: Root filename
            file_ext: File extension
            
        Returns:
            str: Alternative filename
        """
        return f"{file_root}_{hashlib.md5(str(file_root).encode()).hexdigest()[:8]}{file_ext}"

class ProductS3Storage(S3Boto3Storage):
    """Custom S3 storage for product files."""
    
    location = 'products'
    file_overwrite = False
    default_acl = 'public-read'
    querystring_auth = False

    def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
        """
        Return a filename that's free on the target storage system.
        
        Args:
            name: Desired filename
            max_length: Maximum length for filename
            
        Returns:
            str: Available filename
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        
        # Add hash to filename
        file_hash = hashlib.md5(
            f"{file_root}{timezone.now().timestamp()}".encode()
        ).hexdigest()[:8]
        
        return os.path.join(dir_name, f"{file_root}_{file_hash}{file_ext}")

class ProductImageField:
    """Custom field for handling product images."""

    def __init__(self, instance: Any, field: str):
        """
        Initialize image field.
        
        Args:
            instance: Model instance
            field: Field name
        """
        self.instance = instance
        self.field = field
        self.storage = (
            ProductS3Storage()
            if hasattr(settings, 'USE_S3')
            else ProductImageStorage()
        )

    def save(self, file: UploadedFile) -> str:
        """
        Save image file.
        
        Args:
            file: Uploaded file
            
        Returns:
            str: Saved file path
        """
        # Generate path
        file_path = self._get_file_path(file.name)
        
        # Process image
        processed_image = self._process_image(file)
        
        # Save file
        file_path = self.storage.save(file_path, processed_image)
        
        # Generate thumbnails
        self._generate_thumbnails(file_path)
        
        return file_path

    def _get_file_path(self, filename: str) -> str:
        """
        Get file path for saving.
        
        Args:
            filename: Original filename
            
        Returns:
            str: File path
        """
        # Clean filename
        filename = self.storage.get_valid_name(filename)
        
        # Organize by date
        from django.utils import timezone
        date_path = timezone.now().strftime('%Y/%m/%d')
        
        # Include model info in path
        model_name = self.instance._meta.model_name
        
        return os.path.join(
            model_name,
            date_path,
            filename
        )

    def _process_image(self, file: UploadedFile) -> Any:
        """
        Process uploaded image.
        
        Args:
            file: Uploaded file
            
        Returns:
            Any: Processed image
        """
        from PIL import Image
        from io import BytesIO
        
        # Open image
        img = Image.open(file)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        max_size = getattr(settings, 'PRODUCT_IMAGE_MAX_SIZE', (2000, 2000))
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        # Optimize
        output = BytesIO()
        img.save(
            output,
            format='JPEG',
            quality=85,
            optimize=True
        )
        
        return output

    def _generate_thumbnails(self, file_path: str) -> None:
        """
        Generate image thumbnails.
        
        Args:
            file_path: Original file path
        """
        from PIL import Image
        from io import BytesIO
        
        # Thumbnail sizes
        sizes = {
            'small': (200, 200),
            'medium': (400, 400),
            'large': (800, 800)
        }
        
        # Open original image
        with self.storage.open(file_path) as f:
            img = Image.open(f)
            
            for size_name, dimensions in sizes.items():
                # Create thumbnail
                thumb = img.copy()
                thumb.thumbnail(dimensions, Image.LANCZOS)
                
                # Save thumbnail
                output = BytesIO()
                thumb.save(
                    output,
                    format='JPEG',
                    quality=85,
                    optimize=True
                )
                
                # Generate thumbnail path
                dir_name = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                thumb_path = os.path.join(
                    dir_name,
                    'thumbnails',
                    f"{size_name}_{file_name}"
                )
                
                # Save to storage
                self.storage.save(thumb_path, output)

def get_product_image_path(instance: Any, filename: str) -> str:
    """
    Get upload path for product images.
    
    Args:
        instance: Model instance
        filename: Original filename
        
    Returns:
        str: Upload path
    """
    return ProductImageField(instance, 'image').save(filename)
