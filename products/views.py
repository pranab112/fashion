from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Product, Category, Brand, Tag
from .filters import ProductFilter

class ProductListView(ListView):
    """Base view for displaying products."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 24
    
    def get_queryset(self):
        """Get active products with related fields."""
        return Product.objects.active().with_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['colors'] = {
            'black': '#000000',
            'white': '#FFFFFF',
            'red': '#FF0000',
            'blue': '#0000FF',
            'green': '#008000',
            'yellow': '#FFFF00',
            'pink': '#FFC0CB',
            'purple': '#800080',
            'orange': '#FFA500',
            'gray': '#808080'
        }
        context['sizes'] = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        return context

class FeaturedProductListView(ProductListView):
    """View for displaying featured products."""
    
    def get_queryset(self):
        """Get active featured products."""
        return super().get_queryset().filter(is_featured=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Featured Products'
        return context

class NewArrivalsListView(ProductListView):
    """View for displaying new arrival products."""
    
    def get_queryset(self):
        """Get active new arrival products."""
        return super().get_queryset().filter(is_new_arrival=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Arrivals'
        return context

class ProductSearchView(ProductListView):
    """View for searching products."""
    
    def get_queryset(self):
        """Filter products based on search query."""
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            # Basic search
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
            
            # Apply filters if any
            filter = ProductFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['filter'] = ProductFilter(self.request.GET, queryset=self.get_queryset())
        return context

class CategoryListView(ListView):
    """View for displaying product categories."""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """Get active root categories."""
        return Category.objects.filter(is_active=True, parent=None)

class CategoryDetailView(DetailView):
    """View for displaying category details and its products."""
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get products from this category and its subcategories
        try:
            category_ids = self.object.get_descendants(include_self=True).values_list('id', flat=True)
            context['products'] = Product.objects.active().filter(category_id__in=category_ids).with_related()
        except Exception:
            # Fallback to simple category filter
            context['products'] = Product.objects.active().filter(category=self.object).with_related()
        
        # Add site name for template
        context['site_name'] = 'Fashion Store'
        
        return context

class BrandListView(ListView):
    """View for displaying product brands."""
    model = Brand
    template_name = 'products/brand_list.html'
    context_object_name = 'brands'
    
    def get_queryset(self):
        """Get active brands."""
        return Brand.objects.filter(is_active=True)

class BrandDetailView(DetailView):
    """View for displaying brand details and its products."""
    model = Brand
    template_name = 'products/brand_detail.html'
    context_object_name = 'brand'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.active()
        return context

class TagListView(ListView):
    """View for displaying product tags."""
    model = Tag
    template_name = 'products/tag_list.html'
    context_object_name = 'tags'

class TagDetailView(DetailView):
    """View for displaying tag details and its products."""
    model = Tag
    template_name = 'products/tag_detail.html'
    context_object_name = 'tag'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.active()
        return context

class ProductDetailView(DetailView):
    """View for displaying product details."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        """Get active products with related fields."""
        return Product.objects.active().with_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related products
        context['related_products'] = (
            Product.objects.active()
            .filter(category=self.object.category)
            .exclude(id=self.object.id)[:4]
        )
        return context
