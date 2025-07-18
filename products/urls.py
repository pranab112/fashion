from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('featured/', views.FeaturedProductListView.as_view(), name='featured'),
    path('new-arrivals/', views.NewArrivalsListView.as_view(), name='new_arrivals'),
    path('sale/', views.ProductListView.as_view(), name='sale'),
    path('premium/', views.ProductListView.as_view(), name='premium'),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
