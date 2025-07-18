"""
Search functionality for the products app.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from django.db.models import Q, F, Value, FloatField
from django.db.models.functions import Coalesce, Greatest
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity
)
from django.utils import timezone
from django.conf import settings

from .models import Product, Category, Brand, SearchQuery as SearchQueryModel
from .cache import ProductCache
from .constants import (
    SEARCH_BOOST_FIELDS,
    MIN_SEARCH_LENGTH,
    MAX_SEARCH_LENGTH,
    MAX_SEARCH_SUGGESTIONS
)

logger = logging.getLogger(__name__)

class ProductSearch:
    """Product search functionality."""

    @staticmethod
    def search(
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        page_size: int = 24
    ) -> Tuple[List[Product], int]:
        """
        Search products.
        
        Args:
            query: Search query
            filters: Optional filters
            sort: Sort option
            page: Page number
            page_size: Results per page
            
        Returns:
            Tuple[List[Product], int]: Search results and total count
        """
        try:
            # Validate query
            if not MIN_SEARCH_LENGTH <= len(query) <= MAX_SEARCH_LENGTH:
                return [], 0
            
            # Create search vectors
            search_vector = (
                SearchVector('name', weight='A') +
                SearchVector('description', weight='B') +
                SearchVector('brand__name', weight='C') +
                SearchVector('category__name', weight='D')
            )
            
            # Create search query
            search_query = SearchQuery(query)
            
            # Get base queryset
            queryset = Product.objects.filter(is_active=True)
            
            # Apply search ranking
            queryset = queryset.annotate(
                search_rank=SearchRank(search_vector, search_query),
                name_similarity=TrigramSimilarity('name', query),
                brand_similarity=TrigramSimilarity('brand__name', query),
                relevance=Greatest(
                    'search_rank',
                    F('name_similarity') * Value(0.8, FloatField()),
                    F('brand_similarity') * Value(0.6, FloatField())
                )
            ).filter(
                Q(search_rank__gt=0.1) |
                Q(name_similarity__gt=0.1) |
                Q(brand_similarity__gt=0.1)
            )
            
            # Apply filters
            if filters:
                queryset = ProductSearch.apply_filters(queryset, filters)
            
            # Apply sorting
            queryset = ProductSearch.apply_sorting(queryset, sort)
            
            # Get total count
            total = queryset.count()
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            results = queryset[start:end]
            
            # Track search query
            ProductSearch.track_search(query, total > 0)
            
            return results, total
            
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return [], 0

    @staticmethod
    def apply_filters(queryset: Any, filters: Dict[str, Any]) -> Any:
        """
        Apply filters to search results.
        
        Args:
            queryset: Product queryset
            filters: Filter parameters
            
        Returns:
            Any: Filtered queryset
        """
        # Category filter
        if category_id := filters.get('category'):
            queryset = queryset.filter(
                Q(category_id=category_id) |
                Q(category__parent_id=category_id)
            )
        
        # Brand filter
        if brand_id := filters.get('brand'):
            queryset = queryset.filter(brand_id=brand_id)
        
        # Price range filter
        if min_price := filters.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := filters.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)
        
        # Size filter
        if sizes := filters.get('sizes', []):
            queryset = queryset.filter(available_sizes__in=sizes)
        
        # Color filter
        if colors := filters.get('colors', []):
            queryset = queryset.filter(available_colors__in=colors)
        
        # Tag filter
        if tags := filters.get('tags', []):
            queryset = queryset.filter(tags__name__in=tags)
        
        # Rating filter
        if min_rating := filters.get('min_rating'):
            queryset = queryset.filter(average_rating__gte=min_rating)
        
        # Stock filter
        if filters.get('in_stock'):
            queryset = queryset.filter(stock__gt=0)
        
        # Sale filter
        if filters.get('on_sale'):
            queryset = queryset.filter(is_on_sale=True)
        
        return queryset

    @staticmethod
    def apply_sorting(queryset: Any, sort: Optional[str] = None) -> Any:
        """
        Apply sorting to search results.
        
        Args:
            queryset: Product queryset
            sort: Sort option
            
        Returns:
            Any: Sorted queryset
        """
        if sort == 'price_asc':
            return queryset.order_by('price', '-relevance')
        elif sort == 'price_desc':
            return queryset.order_by('-price', '-relevance')
        elif sort == 'name_asc':
            return queryset.order_by('name', '-relevance')
        elif sort == 'name_desc':
            return queryset.order_by('-name', '-relevance')
        elif sort == 'newest':
            return queryset.order_by('-created_at', '-relevance')
        elif sort == 'popular':
            return queryset.order_by('-view_count', '-relevance')
        elif sort == 'rating':
            return queryset.order_by('-average_rating', '-relevance')
        
        # Default sort by relevance
        return queryset.order_by('-relevance')

    @staticmethod
    def get_suggestions(query: str) -> List[str]:
        """
        Get search suggestions.
        
        Args:
            query: Search query
            
        Returns:
            List[str]: Search suggestions
        """
        try:
            # Check cache first
            suggestions = ProductCache.get_search_suggestions(query)
            if suggestions is not None:
                return suggestions
            
            # Get suggestions from database
            suggestions = []
            
            # Add product name suggestions
            product_suggestions = Product.objects.filter(
                name__icontains=query,
                is_active=True
            ).values_list(
                'name',
                flat=True
            ).distinct()[:MAX_SEARCH_SUGGESTIONS]
            suggestions.extend(product_suggestions)
            
            # Add brand name suggestions
            brand_suggestions = Brand.objects.filter(
                name__icontains=query,
                is_active=True
            ).values_list(
                'name',
                flat=True
            ).distinct()[:MAX_SEARCH_SUGGESTIONS]
            suggestions.extend(brand_suggestions)
            
            # Add category name suggestions
            category_suggestions = Category.objects.filter(
                name__icontains=query,
                is_active=True
            ).values_list(
                'name',
                flat=True
            ).distinct()[:MAX_SEARCH_SUGGESTIONS]
            suggestions.extend(category_suggestions)
            
            # Remove duplicates and limit results
            suggestions = list(set(suggestions))[:MAX_SEARCH_SUGGESTIONS]
            
            # Cache suggestions
            ProductCache.set_search_suggestions(query, suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []

    @staticmethod
    def track_search(query: str, has_results: bool) -> None:
        """
        Track search query.
        
        Args:
            query: Search query
            has_results: Whether search returned results
        """
        try:
            # Update or create search query record
            search_query, created = SearchQueryModel.objects.get_or_create(
                query=query.lower(),
                defaults={
                    'count': 1,
                    'last_searched': timezone.now(),
                    'success_rate': 100 if has_results else 0
                }
            )
            
            if not created:
                # Update existing record
                search_query.count += 1
                search_query.last_searched = timezone.now()
                search_query.success_rate = (
                    (search_query.success_rate * (search_query.count - 1) +
                     (100 if has_results else 0)) / search_query.count
                )
                search_query.save()
            
        except Exception as e:
            logger.error(f"Error tracking search query: {str(e)}")

    @staticmethod
    def get_popular_searches(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular search queries.
        
        Args:
            limit: Number of queries to return
            
        Returns:
            List[Dict[str, Any]]: Popular searches
        """
        try:
            return SearchQueryModel.objects.filter(
                success_rate__gt=0
            ).order_by(
                '-count'
            ).values(
                'query',
                'count',
                'success_rate'
            )[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            return []

    @staticmethod
    def get_related_searches(query: str, limit: int = 5) -> List[str]:
        """
        Get related search queries.
        
        Args:
            query: Search query
            limit: Number of queries to return
            
        Returns:
            List[str]: Related searches
        """
        try:
            return SearchQueryModel.objects.filter(
                query__icontains=query,
                success_rate__gt=0
            ).exclude(
                query=query.lower()
            ).order_by(
                '-count'
            ).values_list(
                'query',
                flat=True
            )[:limit]
            
        except Exception as e:
            logger.error(f"Error getting related searches: {str(e)}")
            return []
