"""
Custom pagination classes for the products app.
"""

from typing import Any, Dict, Optional
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework.response import Response

from .constants import (
    PRODUCTS_PER_PAGE,
    API_PAGE_SIZE,
    API_MAX_PAGE_SIZE
)

class ProductPagination(PageNumberPagination):
    """
    Custom pagination for product listings.
    
    Features:
    - Configurable page size
    - Maximum page size limit
    - Page size query parameter
    - Custom response format
    """
    
    page_size = API_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = API_MAX_PAGE_SIZE
    
    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with custom format.
        
        Args:
            data: Data to paginate
            
        Returns:
            Response: Paginated response
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })
    
    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        """
        Get schema for paginated response.
        
        Args:
            schema: Base schema
            
        Returns:
            Dict: Schema with pagination
        """
        return {
            'type': 'object',
            'properties': {
                'links': {
                    'type': 'object',
                    'properties': {
                        'next': {
                            'type': 'string',
                            'format': 'uri',
                            'nullable': True
                        },
                        'previous': {
                            'type': 'string',
                            'format': 'uri',
                            'nullable': True
                        }
                    }
                },
                'count': {
                    'type': 'integer'
                },
                'total_pages': {
                    'type': 'integer'
                },
                'current_page': {
                    'type': 'integer'
                },
                'results': schema
            }
        }

class ProductLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom limit-offset pagination for products.
    
    Features:
    - Default and maximum limits
    - Custom query parameters
    - Custom response format
    """
    
    default_limit = API_PAGE_SIZE
    max_limit = API_MAX_PAGE_SIZE
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    
    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with custom format.
        
        Args:
            data: Data to paginate
            
        Returns:
            Response: Paginated response
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.count,
            'current_offset': self.offset,
            'current_limit': self.limit,
            'results': data
        })

class ProductCursorPagination(CursorPagination):
    """
    Custom cursor pagination for products.
    
    Features:
    - Ordering by created_at
    - Configurable page size
    - Custom response format
    """
    
    page_size = API_PAGE_SIZE
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data: Any) -> Response:
        """
        Get paginated response with custom format.
        
        Args:
            data: Data to paginate
            
        Returns:
            Response: Paginated response
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'results': data
        })

class CustomPaginator(Paginator):
    """
    Custom paginator with additional features.
    
    Features:
    - Custom page range
    - Ellipsis for long page ranges
    - Page window calculation
    """
    
    def __init__(
        self,
        object_list: Any,
        per_page: int,
        orphans: int = 0,
        allow_empty_first_page: bool = True,
        window: int = 4
    ) -> None:
        """
        Initialize paginator.
        
        Args:
            object_list: Objects to paginate
            per_page: Items per page
            orphans: Number of orphans allowed
            allow_empty_first_page: Whether to allow empty first page
            window: Number of pages to show around current page
        """
        self.window = window
        super().__init__(
            object_list,
            per_page,
            orphans,
            allow_empty_first_page
        )
    
    def get_elided_page_range(
        self,
        number: Optional[int] = None,
        on_each_side: int = 3,
        on_ends: int = 2
    ) -> range:
        """
        Get page range with ellipsis.
        
        Args:
            number: Current page number
            on_each_side: Pages to show on each side
            on_ends: Pages to show on ends
            
        Returns:
            range: Page range
        """
        if number is None:
            number = 1
        
        # Calculate page ranges
        if self.num_pages <= (on_each_side + on_ends) * 2:
            return range(1, self.num_pages + 1)
        
        if number > (1 + on_each_side):
            if number > (self.num_pages - on_each_side):
                # Close to end
                start = self.num_pages - on_each_side * 2 - 1
            else:
                # Middle
                start = number - on_each_side
            
            if number < (self.num_pages - on_each_side):
                if number < (1 + on_each_side):
                    # Close to beginning
                    end = 1 + on_each_side * 2 + 1
                else:
                    # Middle
                    end = number + on_each_side + 1
            else:
                end = self.num_pages + 1
        else:
            start = 1
            end = 1 + on_each_side * 2 + 1
        
        return range(start, end)
    
    def get_page_window(self, number: int) -> Dict[str, Any]:
        """
        Get window of pages around current page.
        
        Args:
            number: Current page number
            
        Returns:
            Dict[str, Any]: Page window information
        """
        window_start = max(number - self.window, 1)
        window_end = min(number + self.window + 1, self.num_pages + 1)
        
        return {
            'page_range': range(window_start, window_end),
            'show_first': window_start > 1,
            'show_last': window_end <= self.num_pages,
            'total_pages': self.num_pages,
            'current_page': number
        }
