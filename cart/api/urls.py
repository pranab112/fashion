from django.urls import path
from .views import (
    CartDetailView,
    CartAddView,
    CartUpdateView,
    CartRemoveView,
    CartClearView
)

app_name = 'cart-api'

urlpatterns = [
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/update/', CartUpdateView.as_view(), name='cart-update'),
    path('cart/remove/', CartRemoveView.as_view(), name='cart-remove'),
    path('cart/clear/', CartClearView.as_view(), name='cart-clear'),
]
