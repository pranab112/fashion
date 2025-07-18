from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AddressViewSet

app_name = 'users_api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
]
