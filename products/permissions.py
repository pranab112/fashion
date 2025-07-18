"""
Custom permissions for the products app.
"""

from typing import Any
from django.contrib.auth.models import User
from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.views import APIView

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow admin users to edit.
    Read-only access for other users.
    """
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admin users
        return request.user and request.user.is_staff

class CanManageProducts(permissions.BasePermission):
    """Permission to manage products."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.change_product')
        )
    
    def has_object_permission(
        self,
        request: HttpRequest,
        view: APIView,
        obj: Any
    ) -> bool:
        """
        Check if user has object permission.
        
        Args:
            request: HTTP request
            view: API view
            obj: Object to check permission for
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.change_product')
        )

class CanModerateReviews(permissions.BasePermission):
    """Permission to moderate product reviews."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.change_review')
        )
    
    def has_object_permission(
        self,
        request: HttpRequest,
        view: APIView,
        obj: Any
    ) -> bool:
        """
        Check if user has object permission.
        
        Args:
            request: HTTP request
            view: API view
            obj: Object to check permission for
            
        Returns:
            bool: True if user has permission
        """
        # Allow users to edit their own reviews
        if obj.user == request.user:
            return True
        
        # Moderators can edit any review
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.change_review')
        )

class CanManageCategories(permissions.BasePermission):
    """Permission to manage product categories."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.change_category')
        )

class CanManageBrands(permissions.BasePermission):
    """Permission to manage product brands."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.change_brand')
        )

class IsVerifiedUser(permissions.BasePermission):
    """Permission for verified users only."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_verified', False)
        )

class HasPurchasedProduct(permissions.BasePermission):
    """Permission for users who have purchased the product."""
    
    def has_object_permission(
        self,
        request: HttpRequest,
        view: APIView,
        obj: Any
    ) -> bool:
        """
        Check if user has object permission.
        
        Args:
            request: HTTP request
            view: API view
            obj: Object to check permission for
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            obj.orderitem_set.filter(
                order__user=request.user,
                order__status='completed'
            ).exists()
        )

class CanViewAnalytics(permissions.BasePermission):
    """Permission to view product analytics."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.view_analytics')
        )

class CanExportData(permissions.BasePermission):
    """Permission to export product data."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.export_data')
        )

class CanImportData(permissions.BasePermission):
    """Permission to import product data."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Check if user has permission.
        
        Args:
            request: HTTP request
            view: API view
            
        Returns:
            bool: True if user has permission
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_perm('products.import_data')
        )
