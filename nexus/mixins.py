from typing import Any, Dict, List, Optional, Type
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .monitoring import Monitoring
from .cache import CacheService
from .analytics import AnalyticsService

class AuditMixin:
    """Mixin to add audit fields to models."""

    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )
    created_by = models.ForeignKey(
        'auth.User',
        verbose_name=_('Created By'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        verbose_name=_('Updated By'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to update audit fields."""
        user = kwargs.pop('user', None)
        if user:
            if not self.pk:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)

class CacheMixin:
    """Mixin to add caching functionality."""

    cache_timeout = 300  # 5 minutes
    cache_prefix = None

    def get_cache_key(self) -> str:
        """Get cache key for the object."""
        if not self.cache_prefix:
            self.cache_prefix = self.__class__.__name__.lower()
        return f"{self.cache_prefix}:{self.pk}"

    def cache_data(self) -> Dict:
        """Get data to cache."""
        return {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
        }

    def save(self, *args, **kwargs):
        """Override save to update cache."""
        super().save(*args, **kwargs)
        CacheService.set_cache(
            self.get_cache_key(),
            self.cache_data(),
            timeout=self.cache_timeout
        )

    def delete(self, *args, **kwargs):
        """Override delete to clear cache."""
        CacheService.delete_cache(self.get_cache_key())
        super().delete(*args, **kwargs)

class MonitoringMixin:
    """Mixin to add monitoring functionality to views."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Override dispatch to add monitoring."""
        with Monitoring.monitor_view(
            view_name=self.__class__.__name__,
            request=request
        ):
            return super().dispatch(request, *args, **kwargs)

class AnalyticsMixin:
    """Mixin to add analytics tracking to views."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Override dispatch to track analytics."""
        response = super().dispatch(request, *args, **kwargs)
        
        # Track page view
        if request.method == 'GET':
            AnalyticsService.track_page_view(
                path=request.path,
                user_id=request.user.id if request.user.is_authenticated else None,
                metadata={
                    'referrer': request.META.get('HTTP_REFERER'),
                    'user_agent': request.META.get('HTTP_USER_AGENT')
                }
            )
        
        return response

class PermissionRequiredMixin:
    """Mixin to check permissions for views."""

    permission_required: Optional[str] = None
    permission_denied_message = _("You don't have permission to access this.")

    def has_permission(self) -> bool:
        """Check if user has required permission."""
        if not self.permission_required:
            return True
        
        return self.request.user.has_perm(self.permission_required)

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Override dispatch to check permissions."""
        if not self.has_permission():
            raise PermissionDenied(self.permission_denied_message)
        return super().dispatch(request, *args, **kwargs)

class OwnershipRequiredMixin:
    """Mixin to check object ownership."""

    def has_ownership(self, obj: Any) -> bool:
        """Check if user owns the object."""
        return (
            hasattr(obj, 'user') and
            obj.user == self.request.user
        )

    def get_object(self, *args, **kwargs):
        """Override get_object to check ownership."""
        obj = super().get_object(*args, **kwargs)
        if not self.has_ownership(obj):
            raise PermissionDenied(
                _("You don't have permission to access this object.")
            )
        return obj

class ViewSetMixin(ModelViewSet):
    """Mixin for common ViewSet functionality."""

    def get_serializer_context(self) -> Dict:
        """Add additional context to serializer."""
        context = super().get_serializer_context()
        context.update({
            'user': self.request.user,
            'request': self.request
        })
        return context

    def perform_create(self, serializer: Any) -> None:
        """Override create to add user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: Any) -> None:
        """Override update to add user."""
        serializer.save(updated_by=self.request.user)

class SoftDeleteMixin:
    """Mixin to add soft delete functionality."""

    is_deleted = models.BooleanField(
        _('Is Deleted'),
        default=False,
        db_index=True
    )
    deleted_at = models.DateTimeField(
        _('Deleted At'),
        null=True,
        blank=True
    )
    deleted_by = models.ForeignKey(
        'auth.User',
        verbose_name=_('Deleted By'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_deleted'
    )

    class Meta:
        abstract = True

    def delete(self, user=None, *args, **kwargs):
        """Override delete for soft deletion."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def hard_delete(self, *args, **kwargs):
        """Permanently delete the object."""
        super().delete(*args, **kwargs)

class SearchMixin:
    """Mixin to add search functionality."""

    search_fields: List[str] = []
    search_param: str = 'q'

    def get_queryset(self):
        """Override queryset to add search."""
        queryset = super().get_queryset()
        search_term = self.request.GET.get(self.search_param)
        
        if search_term and self.search_fields:
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_term})
            queryset = queryset.filter(query)
        
        return queryset

class VersioningMixin:
    """Mixin to add API versioning."""

    def get_serializer_class(self):
        """Get serializer class based on version."""
        version = self.request.version
        
        try:
            return self.serializer_classes[version]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

class BulkOperationsMixin:
    """Mixin to add bulk operation support."""

    def bulk_create(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle bulk create operation."""
        serializer = self.get_serializer(
            data=request.data,
            many=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def bulk_update(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handle bulk update operation."""
        serializer = self.get_serializer(
            self.get_queryset().filter(
                id__in=[item['id'] for item in request.data]
            ),
            data=request.data,
            many=True,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)

    def perform_bulk_create(self, serializer: Any) -> None:
        """Perform bulk create operation."""
        serializer.save()

    def perform_bulk_update(self, serializer: Any) -> None:
        """Perform bulk update operation."""
        serializer.save()
