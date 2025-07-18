"""
API views for the products app.
"""

from typing import Any, Dict, List, Optional
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from .models import (
    Product,
    Category,
    Brand,
    Review,
    ProductView,
    SearchQuery
)
from .serializers import (
    ProductSerializer,
    ProductListSerializer,
    CategorySerializer,
    BrandSerializer,
    ReviewSerializer,
    ProductViewSerializer,
    SearchQuerySerializer,
    ProductExportSerializer,
    ProductImportSerializer
)
from .filters import ProductFilter, CategoryFilter, BrandFilter, ReviewFilter
from .pagination import ProductPagination
from .permissions import (
    IsAdminOrReadOnly,
    CanManageProducts,
    CanModerateReviews,
    IsVerifiedUser,
    HasPurchasedProduct
)
from .services import ProductService

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model."""
    
    queryset = Product.objects.active().with_related()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    ordering_fields = [
        'name',
        'price',
        'created_at',
        'view_count',
        'average_rating'
    ]
    
    def get_serializer_class(self) -> Any:
        """Get appropriate serializer class."""
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'export':
            return ProductExportSerializer
        if self.action == 'import_products':
            return ProductImportSerializer
        return ProductSerializer
    
    def get_queryset(self) -> QuerySet:
        """Get base queryset."""
        queryset = super().get_queryset()
        
        # Apply filters from request
        filters = self.request.GET.dict()
        if filters:
            queryset = ProductService.filter_products(queryset, filters)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request: Any, pk: Any = None) -> Response:
        """Add product to user's wishlist."""
        product = self.get_object()
        request.user.wishlist.add(product)
        return Response({'status': 'added to wishlist'})
    
    @action(detail=True, methods=['post'])
    def remove_from_wishlist(self, request: Any, pk: Any = None) -> Response:
        """Remove product from user's wishlist."""
        product = self.get_object()
        request.user.wishlist.remove(product)
        return Response({'status': 'removed from wishlist'})
    
    @action(detail=False, methods=['get'])
    def export(self, request: Any) -> Response:
        """Export products data."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def import_products(self, request: Any) -> Response:
        """Import products from data."""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    
    @action(detail=True)
    def products(self, request: Any, pk: Any = None) -> Response:
        """Get products in category."""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            status='active'
        )
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class BrandViewSet(viewsets.ModelViewSet):
    """ViewSet for Brand model."""
    
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BrandFilter
    search_fields = ['name', 'description']
    
    @action(detail=True)
    def products(self, request: Any, pk: Any = None) -> Response:
        """Get products by brand."""
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand,
            status='active'
        )
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class ReviewViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """ViewSet for Review model."""
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter
    
    def get_permissions(self) -> List[Any]:
        """Get appropriate permissions."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [CanModerateReviews()]
        if self.action == 'create':
            return [IsVerifiedUser(), HasPurchasedProduct()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer: Any) -> None:
        """Create new review."""
        serializer.save(user=self.request.user)

class SearchQueryViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """ViewSet for SearchQuery model."""
    
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=False)
    def popular(self, request: Any) -> Response:
        """Get popular search queries."""
        queries = self.get_queryset().order_by('-count')[:10]
        serializer = self.get_serializer(queries, many=True)
        return Response(serializer.data)

class ProductViewViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """ViewSet for ProductView model."""
    
    queryset = ProductView.objects.all()
    serializer_class = ProductViewSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self) -> QuerySet:
        """Get filtered queryset."""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
    
    @action(detail=False)
    def analytics(self, request: Any) -> Response:
        """Get view analytics."""
        analytics = ProductService.get_view_analytics(
            start_date=request.query_params.get('start_date'),
            end_date=request.query_params.get('end_date')
        )
        return Response(analytics)
