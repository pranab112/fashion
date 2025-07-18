from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any, Optional
from collections import OrderedDict
from .constants import PaginationConstants

class StandardPagination(PageNumberPagination):
    """Standard pagination for most views."""

    page_size = PaginationConstants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = PaginationConstants.MAX_PAGE_SIZE
    page_query_param = 'page'

    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with metadata.
        
        Args:
            data: Serialized data
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.get_page_size(self.request)),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        """
        Get schema for paginated response.
        
        Args:
            schema: Response schema
        """
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'description': _('Total number of items')
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('URL for next page')
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('URL for previous page')
                },
                'page_size': {
                    'type': 'integer',
                    'description': _('Number of items per page')
                },
                'current_page': {
                    'type': 'integer',
                    'description': _('Current page number')
                },
                'total_pages': {
                    'type': 'integer',
                    'description': _('Total number of pages')
                },
                'results': schema,
            }
        }

class LargeResultSetPagination(LimitOffsetPagination):
    """Pagination for large result sets."""

    default_limit = 50
    max_limit = 500
    limit_query_param = 'limit'
    offset_query_param = 'offset'

    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with metadata.
        
        Args:
            data: Serialized data
        """
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('limit', self.limit),
            ('offset', self.offset),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        """
        Get schema for paginated response.
        
        Args:
            schema: Response schema
        """
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'description': _('Total number of items')
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('URL for next page')
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('URL for previous page')
                },
                'limit': {
                    'type': 'integer',
                    'description': _('Number of items per page')
                },
                'offset': {
                    'type': 'integer',
                    'description': _('Index of first item')
                },
                'results': schema,
            }
        }

class CursorBasedPagination(CursorPagination):
    """Cursor-based pagination for time-based ordering."""

    page_size = 20
    ordering = '-created_at'
    cursor_query_param = 'cursor'

    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with metadata.
        
        Args:
            data: Serialized data
        """
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.page_size),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        """
        Get schema for paginated response.
        
        Args:
            schema: Response schema
        """
        return {
            'type': 'object',
            'properties': {
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('URL for next page')
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('URL for previous page')
                },
                'page_size': {
                    'type': 'integer',
                    'description': _('Number of items per page')
                },
                'results': schema,
            }
        }

class ProductPagination(StandardPagination):
    """Pagination for product listings."""

    page_size = 24  # Common grid size (3x8, 4x6, etc.)
    page_size_query_param = 'page_size'
    max_page_size = 96

    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with additional product metadata.
        
        Args:
            data: Serialized data
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.get_page_size(self.request)),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('filters', self.get_filter_metadata()),
            ('sort_options', self.get_sort_options()),
            ('results', data)
        ]))

    def get_filter_metadata(self) -> Dict:
        """Get available filter options."""
        queryset = self.page.paginator.object_list
        return {
            'price_range': {
                'min': queryset.aggregate(min=Min('price'))['min'],
                'max': queryset.aggregate(max=Max('price'))['max']
            },
            'categories': self.get_category_filters(queryset),
            'brands': self.get_brand_filters(queryset),
            'sizes': self.get_size_filters(queryset),
            'colors': self.get_color_filters(queryset)
        }

    def get_sort_options(self) -> List[Dict]:
        """Get available sort options."""
        return [
            {'value': 'price_asc', 'label': _('Price: Low to High')},
            {'value': 'price_desc', 'label': _('Price: High to Low')},
            {'value': 'newest', 'label': _('Newest First')},
            {'value': 'popular', 'label': _('Most Popular')},
            {'value': 'rating', 'label': _('Highest Rated')}
        ]

    def get_category_filters(self, queryset) -> List[Dict]:
        """Get category filter options."""
        return (
            queryset
            .values('category__id', 'category__name')
            .annotate(count=Count('id'))
            .order_by('category__name')
        )

    def get_brand_filters(self, queryset) -> List[Dict]:
        """Get brand filter options."""
        return (
            queryset
            .values('brand__id', 'brand__name')
            .annotate(count=Count('id'))
            .order_by('brand__name')
        )

    def get_size_filters(self, queryset) -> List[Dict]:
        """Get size filter options."""
        return (
            queryset
            .values('variants__size')
            .annotate(count=Count('id'))
            .order_by('variants__size')
        )

    def get_color_filters(self, queryset) -> List[Dict]:
        """Get color filter options."""
        return (
            queryset
            .values('variants__color')
            .annotate(count=Count('id'))
            .order_by('variants__color')
        )

class SearchPagination(StandardPagination):
    """Pagination for search results."""

    page_size = 20
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with search metadata.
        
        Args:
            data: Serialized data
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.get_page_size(self.request)),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('search_time', self.get_search_time()),
            ('suggestions', self.get_search_suggestions()),
            ('results', data)
        ]))

    def get_search_time(self) -> Optional[float]:
        """Get search execution time."""
        return getattr(self.request, 'search_time', None)

    def get_search_suggestions(self) -> List[str]:
        """Get search suggestions."""
        return getattr(self.request, 'search_suggestions', [])
