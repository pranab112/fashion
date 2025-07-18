from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured

class ProductQuerySetMixin:
    """Mixin for product-related views to handle common queryset operations."""
    
    def get_queryset(self):
        """
        Get the base queryset for product views.
        Ensures only active products are shown and related fields are prefetched.
        """
        if not hasattr(self, 'model'):
            raise ImproperlyConfigured(
                "%(cls)s is missing a model. Define "
                "%(cls)s.model or override %(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
            
        return self.model.objects.active().with_related()

class FilterMixin:
    """Mixin for handling common filtering operations."""
    
    def get_filters_from_request(self, request):
        """Extract filter parameters from request."""
        filters = {}
        
        # Price range
        price_min = request.GET.get('price_min')
        if price_min:
            filters['base_price__gte'] = float(price_min)
            
        price_max = request.GET.get('price_max')
        if price_max:
            filters['base_price__lte'] = float(price_max)
            
        # Categories
        category = request.GET.get('category')
        if category:
            filters['category__slug'] = category
            
        # Brands
        brand = request.GET.get('brand')
        if brand:
            filters['brand__slug'] = brand
            
        # Tags
        tag = request.GET.get('tag')
        if tag:
            filters['tags__slug'] = tag
            
        # Gender
        gender = request.GET.get('gender')
        if gender:
            filters['gender'] = gender
            
        # Sale items
        on_sale = request.GET.get('on_sale')
        if on_sale:
            filters['discount_percentage__gt'] = 0
            
        return filters
    
    def get_search_query(self, request):
        """Extract search query from request."""
        q = request.GET.get('q')
        if q:
            return Q(name__icontains=q) | \
                   Q(description__icontains=q) | \
                   Q(category__name__icontains=q) | \
                   Q(brand__name__icontains=q) | \
                   Q(tags__name__icontains=q)
        return Q()

class SortMixin:
    """Mixin for handling sorting operations."""
    
    SORT_OPTIONS = {
        'price_asc': 'base_price',
        'price_desc': '-base_price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
        'oldest': 'created_at',
    }
    
    def get_sort_field(self, request):
        """Get sort field from request."""
        sort = request.GET.get('sort', 'newest')
        return self.SORT_OPTIONS.get(sort, '-created_at')
