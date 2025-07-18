from django_filters import rest_framework as filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from typing import Any, Dict, List
from decimal import Decimal

class ProductFilter(filters.FilterSet):
    """Filter set for products."""

    # Price range filters
    min_price = filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        help_text=_('Minimum price')
    )
    max_price = filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        help_text=_('Maximum price')
    )

    # Category filters
    category = filters.CharFilter(
        field_name='category__name',
        lookup_expr='iexact',
        help_text=_('Category name')
    )
    category_id = filters.NumberFilter(
        field_name='category__id',
        help_text=_('Category ID')
    )

    # Brand filters
    brand = filters.CharFilter(
        field_name='brand__name',
        lookup_expr='iexact',
        help_text=_('Brand name')
    )
    brand_id = filters.NumberFilter(
        field_name='brand__id',
        help_text=_('Brand ID')
    )

    # Size and color filters
    size = filters.CharFilter(
        field_name='variants__size',
        help_text=_('Product size')
    )
    color = filters.CharFilter(
        field_name='variants__color',
        help_text=_('Product color')
    )

    # Stock status filter
    in_stock = filters.BooleanFilter(
        method='filter_in_stock',
        help_text=_('Filter by stock availability')
    )

    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        help_text=_('Search in name and description')
    )

    # Sort options
    SORT_OPTIONS = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
        'oldest': 'created_at',
        'popular': '-view_count',
        'rating': '-average_rating',
    }

    sort_by = filters.ChoiceFilter(
        choices=[(k, k) for k in SORT_OPTIONS.keys()],
        method='filter_sort_by',
        help_text=_('Sort results')
    )

    def filter_in_stock(self, queryset, name, value):
        """Filter products by stock availability."""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)

    def filter_search(self, queryset, name, value):
        """Search in product name and description."""
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(brand__name__icontains=value)
            )
        return queryset

    def filter_sort_by(self, queryset, name, value):
        """Sort products based on selected option."""
        order_by = self.SORT_OPTIONS.get(value)
        if order_by:
            return queryset.order_by(order_by)
        return queryset

    class Meta:
        model = 'products.Product'
        fields = [
            'min_price', 'max_price', 'category', 'category_id',
            'brand', 'brand_id', 'size', 'color', 'in_stock',
            'search', 'sort_by'
        ]

class OrderFilter(filters.FilterSet):
    """Filter set for orders."""

    # Date range filters
    start_date = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text=_('Start date')
    )
    end_date = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text=_('End date')
    )

    # Status filter
    status = filters.ChoiceFilter(
        choices=[
            ('pending', _('Pending')),
            ('processing', _('Processing')),
            ('shipped', _('Shipped')),
            ('delivered', _('Delivered')),
            ('cancelled', _('Cancelled')),
        ],
        help_text=_('Order status')
    )

    # Amount range filters
    min_amount = filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='gte',
        help_text=_('Minimum order amount')
    )
    max_amount = filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='lte',
        help_text=_('Maximum order amount')
    )

    class Meta:
        model = 'orders.Order'
        fields = [
            'start_date', 'end_date', 'status',
            'min_amount', 'max_amount'
        ]

class ReviewFilter(filters.FilterSet):
    """Filter set for reviews."""

    # Rating range filters
    min_rating = filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        help_text=_('Minimum rating')
    )
    max_rating = filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        help_text=_('Maximum rating')
    )

    # Product filter
    product = filters.NumberFilter(
        field_name='product__id',
        help_text=_('Product ID')
    )

    # Date range filters
    start_date = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text=_('Start date')
    )
    end_date = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text=_('End date')
    )

    class Meta:
        model = 'products.Review'
        fields = [
            'min_rating', 'max_rating', 'product',
            'start_date', 'end_date'
        ]

class UserFilter(filters.FilterSet):
    """Filter set for users."""

    # Date joined range filters
    joined_after = filters.DateFilter(
        field_name='date_joined',
        lookup_expr='gte',
        help_text=_('Joined after date')
    )
    joined_before = filters.DateFilter(
        field_name='date_joined',
        lookup_expr='lte',
        help_text=_('Joined before date')
    )

    # Status filter
    is_active = filters.BooleanFilter(
        help_text=_('Active status')
    )

    # Role filter
    role = filters.CharFilter(
        method='filter_role',
        help_text=_('User role')
    )

    def filter_role(self, queryset, name, value):
        """Filter users by role."""
        return queryset.filter(groups__name=value)

    class Meta:
        model = 'auth.User'
        fields = ['joined_after', 'joined_before', 'is_active', 'role']

class CategoryFilter(filters.FilterSet):
    """Filter set for categories."""

    # Parent category filter
    parent = filters.NumberFilter(
        field_name='parent__id',
        help_text=_('Parent category ID')
    )

    # Active status filter
    is_active = filters.BooleanFilter(
        help_text=_('Active status')
    )

    # Product count range filters
    min_products = filters.NumberFilter(
        method='filter_min_products',
        help_text=_('Minimum number of products')
    )
    max_products = filters.NumberFilter(
        method='filter_max_products',
        help_text=_('Maximum number of products')
    )

    def filter_min_products(self, queryset, name, value):
        """Filter categories by minimum number of products."""
        return queryset.annotate(
            product_count=Count('products')
        ).filter(product_count__gte=value)

    def filter_max_products(self, queryset, name, value):
        """Filter categories by maximum number of products."""
        return queryset.annotate(
            product_count=Count('products')
        ).filter(product_count__lte=value)

    class Meta:
        model = 'products.Category'
        fields = [
            'parent', 'is_active',
            'min_products', 'max_products'
        ]

class BrandFilter(filters.FilterSet):
    """Filter set for brands."""

    # Active status filter
    is_active = filters.BooleanFilter(
        help_text=_('Active status')
    )

    # Product count range filters
    min_products = filters.NumberFilter(
        method='filter_min_products',
        help_text=_('Minimum number of products')
    )
    max_products = filters.NumberFilter(
        method='filter_max_products',
        help_text=_('Maximum number of products')
    )

    def filter_min_products(self, queryset, name, value):
        """Filter brands by minimum number of products."""
        return queryset.annotate(
            product_count=Count('products')
        ).filter(product_count__gte=value)

    def filter_max_products(self, queryset, name, value):
        """Filter brands by maximum number of products."""
        return queryset.annotate(
            product_count=Count('products')
        ).filter(product_count__lte=value)

    class Meta:
        model = 'products.Brand'
        fields = [
            'is_active',
            'min_products', 'max_products'
        ]
