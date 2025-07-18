from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

def staff_required(view_func):
    """
    Decorator for views that checks that the user is staff,
    redirecting to the login page if necessary.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _('Please log in to access this page.'))
            return redirect('users:login')
        if not request.user.is_staff:
            raise PermissionDenied(_('You do not have permission to access this page.'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def product_owner_required(view_func):
    """
    Decorator for views that checks that the user owns the product
    or is a staff member.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _('Please log in to access this page.'))
            return redirect('users:login')
            
        # Staff can access all products
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
            
        # Get product from view kwargs
        product = kwargs.get('product')
        if not product:
            raise ValueError(_('This decorator requires a product parameter'))
            
        # Check if user owns the product
        if product.seller != request.user:
            raise PermissionDenied(_('You do not have permission to access this product.'))
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def ajax_required(view_func):
    """
    Decorator for views that checks that the request is AJAX.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            raise PermissionDenied(_('This endpoint only accepts AJAX requests.'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
