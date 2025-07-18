from typing import Optional, Dict, Any
from django.utils.translation import gettext_lazy as _

class NexusError(Exception):
    """Base exception for all Nexus application errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ValidationError(NexusError):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = _("Validation error occurred."),
        field: Optional[str] = None,
        code: str = 'validation_error',
        details: Optional[Dict[str, Any]] = None
    ):
        self.field = field
        super().__init__(message, code, details)

class AuthenticationError(NexusError):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str = _("Authentication failed."),
        code: str = 'authentication_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class AuthorizationError(NexusError):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        message: str = _("Permission denied."),
        code: str = 'authorization_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class PaymentError(NexusError):
    """Exception raised for payment processing errors."""

    def __init__(
        self,
        message: str = _("Payment processing failed."),
        code: str = 'payment_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class InventoryError(NexusError):
    """Exception raised for inventory-related errors."""

    def __init__(
        self,
        message: str = _("Inventory operation failed."),
        code: str = 'inventory_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class OrderError(NexusError):
    """Exception raised for order-related errors."""

    def __init__(
        self,
        message: str = _("Order operation failed."),
        code: str = 'order_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class CartError(NexusError):
    """Exception raised for shopping cart errors."""

    def __init__(
        self,
        message: str = _("Cart operation failed."),
        code: str = 'cart_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class ProductError(NexusError):
    """Exception raised for product-related errors."""

    def __init__(
        self,
        message: str = _("Product operation failed."),
        code: str = 'product_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class ShippingError(NexusError):
    """Exception raised for shipping-related errors."""

    def __init__(
        self,
        message: str = _("Shipping operation failed."),
        code: str = 'shipping_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class FileUploadError(NexusError):
    """Exception raised for file upload errors."""

    def __init__(
        self,
        message: str = _("File upload failed."),
        code: str = 'file_upload_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class CacheError(NexusError):
    """Exception raised for caching errors."""

    def __init__(
        self,
        message: str = _("Cache operation failed."),
        code: str = 'cache_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class SearchError(NexusError):
    """Exception raised for search-related errors."""

    def __init__(
        self,
        message: str = _("Search operation failed."),
        code: str = 'search_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class NotificationError(NexusError):
    """Exception raised for notification errors."""

    def __init__(
        self,
        message: str = _("Notification sending failed."),
        code: str = 'notification_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class RateLimitError(NexusError):
    """Exception raised for rate limiting errors."""

    def __init__(
        self,
        message: str = _("Too many requests."),
        code: str = 'rate_limit_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class ConfigurationError(NexusError):
    """Exception raised for configuration errors."""

    def __init__(
        self,
        message: str = _("Configuration error occurred."),
        code: str = 'configuration_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class ThirdPartyServiceError(NexusError):
    """Exception raised for third-party service errors."""

    def __init__(
        self,
        message: str = _("Third-party service error occurred."),
        service: Optional[str] = None,
        code: str = 'third_party_error',
        details: Optional[Dict[str, Any]] = None
    ):
        self.service = service
        super().__init__(message, code, details)

class DatabaseError(NexusError):
    """Exception raised for database errors."""

    def __init__(
        self,
        message: str = _("Database operation failed."),
        code: str = 'database_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class MaintenanceError(NexusError):
    """Exception raised during maintenance mode."""

    def __init__(
        self,
        message: str = _("Service is under maintenance."),
        code: str = 'maintenance_error',
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)

class APIError(NexusError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str = _("API error occurred."),
        code: str = 'api_error',
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        super().__init__(message, code, details)
