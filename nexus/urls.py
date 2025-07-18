from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core app URLs
    path('', include('core.urls', namespace='core')),
    
    # Products app URLs
    path('products/', include('products.urls', namespace='products')),
    path('api/products/', include('products.api.urls')),
    
    # Cart app URLs
    path('cart/', include('cart.urls', namespace='cart')),
    path('api/cart/', include('cart.api.urls')),
    
    # Users app URLs
    path('users/', include('users.urls', namespace='users')),
    path('api/users/', include('users.api.urls')),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
