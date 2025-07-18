from typing import Any, Dict, List, Optional, Union
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from .constants import UserConstants
from .exceptions import AuthorizationError

class BasePermission:
    """Base class for custom permissions."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has permission for this view."""
        raise NotImplementedError

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        """Check if user has permission for this object."""
        raise NotImplementedError

class IsAdmin(BasePermission):
    """Permission class for admin users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name=UserConstants.ROLE_ADMIN).exists()
        )

class IsStaff(BasePermission):
    """Permission class for staff users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name=UserConstants.ROLE_STAFF).exists()
        )

class IsOwner(BasePermission):
    """Permission class for object owners."""

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(obj, 'user') and
            obj.user == request.user
        )

class ReadOnly(BasePermission):
    """Permission class for read-only access."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.method in permissions.SAFE_METHODS

class PermissionManager:
    """Manager class for handling permissions."""

    @staticmethod
    def create_group(
        name: str,
        permissions: List[str],
        description: Optional[str] = None
    ) -> Group:
        """
        Create a new permission group.
        
        Args:
            name: Group name
            permissions: List of permission codenames
            description: Optional group description
        """
        group, created = Group.objects.get_or_create(name=name)
        
        # Add permissions
        for permission_name in permissions:
            app_label, codename = permission_name.split('.')
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type__app_label=app_label
                )
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                raise ValueError(f"Permission {permission_name} does not exist")

        return group

    @staticmethod
    def get_model_permissions(model: Model) -> List[Permission]:
        """Get all permissions for a model."""
        content_type = ContentType.objects.get_for_model(model)
        return Permission.objects.filter(content_type=content_type)

    @staticmethod
    def create_custom_permission(
        codename: str,
        name: str,
        content_type: ContentType
    ) -> Permission:
        """Create a custom permission."""
        return Permission.objects.create(
            codename=codename,
            name=name,
            content_type=content_type
        )

    @staticmethod
    def assign_permissions(
        user_or_group: Union[Model, Group],
        permissions: List[str]
    ) -> None:
        """Assign permissions to user or group."""
        for permission_name in permissions:
            app_label, codename = permission_name.split('.')
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type__app_label=app_label
                )
                if isinstance(user_or_group, Group):
                    user_or_group.permissions.add(permission)
                else:
                    user_or_group.user_permissions.add(permission)
            except Permission.DoesNotExist:
                raise ValueError(f"Permission {permission_name} does not exist")

class ProductPermissions(BasePermission):
    """Permission class for product-related operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        # Allow read operations for all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require staff permissions for write operations
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or
             request.user.groups.filter(name=UserConstants.ROLE_STAFF).exists())
        )

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        # Allow read operations for all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow staff to modify any product
        if request.user.is_staff:
            return True

        # Allow product owner to modify their products
        return bool(
            hasattr(obj, 'seller') and
            obj.seller == request.user
        )

class OrderPermissions(BasePermission):
    """Permission class for order-related operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        # Allow staff to access any order
        if request.user.is_staff:
            return True

        # Allow users to access their own orders
        return obj.user == request.user

class ReviewPermissions(BasePermission):
    """Permission class for review-related operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow staff to moderate reviews
        if request.user.is_staff:
            return True

        # Allow users to modify their own reviews
        return obj.user == request.user

class CartPermissions(BasePermission):
    """Permission class for cart-related operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        return obj.user == request.user

class WishlistPermissions(BasePermission):
    """Permission class for wishlist-related operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        return obj.user == request.user

class AddressPermissions(BasePermission):
    """Permission class for address-related operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        return obj.user == request.user

class PaymentMethodPermissions(BasePermission):
    """Permission class for payment method operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any
    ) -> bool:
        return obj.user == request.user
