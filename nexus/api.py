from typing import Any, Dict, List, Optional, Union
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
import logging
from .monitoring import Monitoring

logger = logging.getLogger(__name__)

class APIResponse:
    """Standard API response format."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: Dict = None
    ) -> Response:
        """
        Create success response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
        """
        response_data = {
            "status": "success",
            "message": message,
            "data": data
        }

        if meta:
            response_data["meta"] = meta

        return Response(
            response_data,
            status=status_code
        )

    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Union[str, List, Dict] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = None
    ) -> Response:
        """
        Create error response.
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            code: Error code for client reference
        """
        response_data = {
            "status": "error",
            "message": message
        }

        if errors:
            response_data["errors"] = errors

        if code:
            response_data["code"] = code

        return Response(
            response_data,
            status=status_code
        )

    @staticmethod
    def paginated_response(
        data: List,
        page: int,
        per_page: int,
        total: int,
        message: str = "Success"
    ) -> Response:
        """
        Create paginated response.
        
        Args:
            data: Page data
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
        """
        return Response({
            "status": "success",
            "message": message,
            "data": data,
            "meta": {
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page
                }
            }
        })

class APIErrorHandler:
    """Handle API errors and exceptions."""

    @staticmethod
    def handle_exception(exc: Exception) -> Response:
        """Handle different types of exceptions."""
        
        # Log the error
        logger.error(
            "API Error",
            exc_info=exc,
            extra={
                'error_type': type(exc).__name__,
                'error_message': str(exc)
            }
        )

        # Handle specific exceptions
        if isinstance(exc, ValidationError):
            return APIErrorHandler.handle_validation_error(exc)
        
        if isinstance(exc, IntegrityError):
            return APIErrorHandler.handle_integrity_error(exc)
        
        if isinstance(exc, Http404):
            return APIErrorHandler.handle_not_found_error(exc)
        
        # Handle unknown errors
        return APIResponse.error(
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_error"
        )

    @staticmethod
    def handle_validation_error(exc: ValidationError) -> Response:
        """Handle validation errors."""
        if hasattr(exc, 'message_dict'):
            errors = exc.message_dict
        else:
            errors = {'error': list(exc.messages)}

        return APIResponse.error(
            message="Validation error",
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="validation_error"
        )

    @staticmethod
    def handle_integrity_error(exc: IntegrityError) -> Response:
        """Handle database integrity errors."""
        return APIResponse.error(
            message="Data integrity error",
            errors=str(exc),
            status_code=status.HTTP_409_CONFLICT,
            code="integrity_error"
        )

    @staticmethod
    def handle_not_found_error(exc: Http404) -> Response:
        """Handle not found errors."""
        return APIResponse.error(
            message="Resource not found",
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found"
        )

class APIUtils:
    """Utility functions for API handling."""

    @staticmethod
    def clean_data(data: Dict) -> Dict:
        """Clean request data."""
        return {
            k: v for k, v in data.items()
            if v is not None and v != ''
        }

    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> None:
        """Validate required fields in request data."""
        missing_fields = [
            field for field in required_fields
            if field not in data or data[field] is None
        ]
        
        if missing_fields:
            raise ValidationError({
                'missing_fields': missing_fields,
                'message': 'Required fields are missing'
            })

    @staticmethod
    def format_validation_errors(errors: Dict) -> Dict:
        """Format validation errors for response."""
        formatted_errors = {}
        
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                formatted_errors[field] = error_list[0]
            else:
                formatted_errors[field] = str(error_list)
        
        return formatted_errors

class APIRateLimit:
    """Rate limiting for API endpoints."""

    def __init__(
        self,
        requests: int = 100,
        window: int = 3600,
        by: str = 'ip'
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests: Number of allowed requests
            window: Time window in seconds
            by: Rate limit by 'ip' or 'user'
        """
        self.requests = requests
        self.window = window
        self.by = by

    def __call__(self, func):
        """Decorator for rate limiting."""
        from functools import wraps
        from django.core.cache import cache
        from django.http import HttpRequest

        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            # Get identifier based on rate limit type
            if self.by == 'user' and request.user.is_authenticated:
                identifier = f"rate_limit:user:{request.user.id}"
            else:
                identifier = f"rate_limit:ip:{request.META.get('REMOTE_ADDR')}"

            # Get current count
            count = cache.get(identifier, 0)

            # Check if limit exceeded
            if count >= self.requests:
                return APIResponse.error(
                    message="Rate limit exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    code="rate_limit_exceeded"
                )

            # Increment count
            cache.set(
                identifier,
                count + 1,
                self.window
            )

            return func(request, *args, **kwargs)

        return wrapper

class APIVersioning:
    """Handle API versioning."""

    @staticmethod
    def get_version(request: HttpRequest) -> str:
        """Get API version from request."""
        # Check header
        version = request.headers.get('X-API-Version')
        if version:
            return version

        # Check query parameter
        version = request.GET.get('version')
        if version:
            return version

        # Default version
        return '1.0'

    @staticmethod
    def is_supported_version(version: str) -> bool:
        """Check if API version is supported."""
        supported_versions = ['1.0', '1.1', '2.0']
        return version in supported_versions

class APIMetrics:
    """Track API metrics."""

    @staticmethod
    def track_request(
        request: HttpRequest,
        response: Response,
        duration: float
    ) -> None:
        """Track API request metrics."""
        metrics = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration': duration,
            'user_id': getattr(request.user, 'id', None),
            'ip': request.META.get('REMOTE_ADDR'),
        }

        # Log metrics
        logger.info('api_request', extra=metrics)

        # Send to monitoring service
        Monitoring.track_api_request(metrics)
