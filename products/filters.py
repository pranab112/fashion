import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, Brand, Tag

class ProductFilter(django_filters.FilterSet):
    """Filter for Product model."""
    
    PRICE_CHOICES = (
        ('', _('Any')),
        ('0-50', _('$0 - $50')),
        ('50-100', _('$50 - $100')),
        ('100-200', _('$100 - $200')),
        ('200-500', _('$200 - $500')),
        ('500+', _('$500+')),
    )
    
    SORT_CHOICES = (
        ('', _('Default')),
        ('price_asc', _('Price: Low to High')),
        ('price_desc', _('Price: High to Low')),
        ('name_asc', _('Name: A to Z')),
        ('name_desc', _('Name: Z to A')),
        ('newest', _('Newest First')),
        ('oldest', _('Oldest First')),
    )
    
    # Basic Filters
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label=_('Category'),
        empty_label=_('All Categories')
    )
    
    brand = django_filters.ModelChoiceFilter(
        queryset=Brand.objects.all(),
        label=_('Brand'),
        empty_label=_('All Brands')
    )
    
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        label=_('Tags')
    )
    
    # Price Range Filter
    price_range = django_filters.ChoiceFilter(
        choices=PRICE_CHOICES,
        label=_('Price Range'),
        method='filter_price_range'
    )
    
    # Custom price range
    min_price = django_filters.NumberFilter(
        field_name='base_price',
        lookup_expr='gte',
        label=_('Min Price')
    )
    max_price = django_filters.NumberFilter(
        field_name='base_price',
        lookup_expr='lte',
        label=_('Max Price')
    )
    
    # Status Filters
    is_on_sale = django_filters.BooleanFilter(
        method='filter_on_sale',
        label=_('On Sale')
    )
    
    is_in_stock = django_filters.BooleanFilter(
        method='filter_in_stock',
        label=_('In Stock')
    )
    
    # Search
    search = django_filters.CharFilter(
        method='filter_search',
        label=_('Search')
    )
    
    # Sorting
    sort = django_filters.ChoiceFilter(
        choices=SORT_CHOICES,
        label=_('Sort By'),
        method='filter_sort'
    )
    
    class Meta:
        model = Product
        fields = [
            'category',
            'brand',
            'tags',
            'gender',
            'price_range',
            'min_price',
            'max_price',
            'is_on_sale',
            'is_in_stock',
            'search',
            'sort'
        ]
    
    def filter_price_range(self, queryset, name, value):
        if not value:
            return queryset
            
        if value == '500+':
            return queryset.filter(base_price__gte=500)
            
        try:
            min_price, max_price = map(float, value.split('-'))
            return queryset.filter(base_price__gte=min_price, base_price__lte=max_price)
        except (ValueError, AttributeError):
            return queryset
    
    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(discount_percentage__gt=0)
        return queryset
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__stock__gt=0).distinct()
        return queryset
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
            
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(category__name__icontains=value) |
            Q(brand__name__icontains=value) |
            Q(tags__name__icontains=value)
        ).distinct()
    
    def filter_sort(self, queryset, name, value):
        if value == 'price_asc':
            return queryset.order_by('base_price')
        elif value == 'price_desc':
            return queryset.order_by('-base_price')
        elif value == 'name_asc':
            return queryset.order_by('name')
        elif value == 'name_desc':
            return queryset.order_by('-name')
        elif value == 'newest':
            return queryset.order_by('-created_at')
        elif value == 'oldest':
            return queryset.order_by('created_at')
        return queryset
