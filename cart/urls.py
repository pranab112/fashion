from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<slug:product_slug>/', views.cart_add, name='add'),
    path('remove/<slug:product_slug>/', views.cart_remove, name='remove'),
    path('update/<slug:product_slug>/', views.cart_update, name='update'),
    path('clear/', views.cart_clear, name='clear'),
    
    # Checkout process
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/review/', views.checkout_review, name='checkout_review'),
    path('checkout/complete/', views.checkout_complete, name='checkout_complete'),
    
    # Wishlist
    path('wishlist/', views.wishlist_detail, name='wishlist'),
    path('wishlist/add/<slug:product_slug>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<slug:product_slug>/', views.wishlist_remove, name='wishlist_remove'),
    
    # API endpoints
    path('api/cart/', views.cart_info, name='api_cart_info'),
    path('api/cart/add/', views.api_cart_add, name='api_cart_add'),
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('api/cart/remove/', views.api_cart_remove, name='api_cart_remove'),
]
