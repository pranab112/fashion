from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'tags', views.TagViewSet)

app_name = 'products-api'

urlpatterns = [
    path('', include(router.urls)),
]
