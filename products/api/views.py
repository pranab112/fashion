from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Product, Category, Brand, Tag
from ..serializers import (
    ProductSerializer,
    ProductListSerializer,
    CategorySerializer,
    BrandSerializer,
    TagSerializer
)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing products."""
    
    queryset = Product.objects.active().with_related()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['category', 'brand', 'gender', 'is_featured', 'is_new_arrival']
    search_fields = ['name', 'description', 'category__name', 'brand__name']
    ordering_fields = ['created_at', 'name', 'base_price']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    @action(detail=False)
    def featured(self, request):
        """Get featured products."""
        products = self.get_queryset().filter(is_featured=True)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def new_arrivals(self, request):
        """Get new arrival products."""
        products = self.get_queryset().filter(is_new_arrival=True)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing categories."""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing brands."""
    
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing tags."""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
