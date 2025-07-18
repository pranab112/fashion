from .models import Cart

def cart(request):
    """Add cart information to the template context."""
    try:
        cart = Cart.objects.get_or_create_from_session(request)
        return {
            'cart': cart,
            'cart_total_items': cart.total_items,
            'cart_subtotal': cart.subtotal,
            'cart_total': cart.total,
        }
    except:
        # Return empty context if there's any error
        return {
            'cart': None,
            'cart_total_items': 0,
            'cart_subtotal': 0,
            'cart_total': 0,
        }
