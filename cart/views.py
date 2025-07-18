from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product, ProductVariant
from .models import Cart, CartItem, Order
from .forms import CartAddProductForm, CheckoutForm

def cart_detail(request):
    """Display the cart contents."""
    cart = Cart.objects.get_or_create_from_session(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_slug):
    """Add a product to the cart."""
    product = get_object_or_404(Product, slug=product_slug, status='active')
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cart = Cart.objects.get_or_create_from_session(request)
        quantity = form.cleaned_data['quantity']
        variant_id = form.cleaned_data.get('variant')
        
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
            cart.add(product, variant, quantity)
        else:
            cart.add(product, None, quantity)
            
        messages.success(request, 'Product added to cart.')
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Product added to cart',
                'cart_total': cart.total_items
            })
            
    return redirect('cart:detail')

@require_POST
def cart_remove(request, product_slug):
    """Remove a product from the cart."""
    product = get_object_or_404(Product, slug=product_slug)
    cart = Cart.objects.get_or_create_from_session(request)
    cart.remove(product)
    
    messages.success(request, 'Product removed from cart.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product removed from cart',
            'cart_total': cart.total_items
        })
        
    return redirect('cart:detail')

@require_POST
def cart_update(request, product_slug):
    """Update product quantity in cart."""
    product = get_object_or_404(Product, slug=product_slug)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cart = Cart.objects.get_or_create_from_session(request)
        quantity = form.cleaned_data['quantity']
        variant_id = form.cleaned_data.get('variant')
        
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
            cart.update(product, variant, quantity)
        else:
            cart.update(product, None, quantity)
            
        messages.success(request, 'Cart updated.')
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Cart updated',
                'cart_total': cart.total_items
            })
            
    return redirect('cart:detail')

@require_POST
def cart_clear(request):
    """Clear all items from cart."""
    cart = Cart.objects.get_or_create_from_session(request)
    cart.clear()
    
    messages.success(request, 'Cart cleared.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Cart cleared',
            'cart_total': 0
        })
        
    return redirect('cart:detail')

@login_required
def checkout(request):
    """Start checkout process."""
    cart = Cart.objects.get_or_create_from_session(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:detail')
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            # Create order items from cart
            for item in cart.items.all():
                order.items.create(
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    price=item.price
                )
                
            # Clear the cart
            cart.clear()
            
            messages.success(request, 'Order placed successfully.')
            return redirect('cart:checkout_complete')
    else:
        form = CheckoutForm(initial={
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })
        
    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'form': form
    })

@login_required
def checkout_shipping(request):
    """Handle shipping information."""
    return render(request, 'cart/checkout_shipping.html')

@login_required
def checkout_payment(request):
    """Handle payment processing."""
    return render(request, 'cart/checkout_payment.html')

@login_required
def checkout_review(request):
    """Review order before completion."""
    return render(request, 'cart/checkout_review.html')

@login_required
def checkout_complete(request):
    """Display order completion page."""
    return render(request, 'cart/checkout_complete.html')

@login_required
def wishlist_detail(request):
    """Display user's wishlist."""
    return render(request, 'cart/wishlist.html')

@login_required
@require_POST
def wishlist_add(request, product_slug):
    """Add product to wishlist."""
    product = get_object_or_404(Product, slug=product_slug)
    request.user.wishlist.add(product)
    
    messages.success(request, 'Product added to wishlist.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to wishlist'
        })
        
    return redirect('cart:wishlist')

@login_required
@require_POST
def wishlist_remove(request, product_slug):
    """Remove product from wishlist."""
    product = get_object_or_404(Product, slug=product_slug)
    request.user.wishlist.remove(product)
    
    messages.success(request, 'Product removed from wishlist.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product removed from wishlist'
        })
        
    return redirect('cart:wishlist')

def cart_info(request):
    """Return cart information as JSON."""
    cart = Cart.objects.get_or_create_from_session(request)
    return JsonResponse({
        'total_items': cart.total_items,
        'subtotal': float(cart.subtotal),
        'total': float(cart.total)
    })

@require_POST
def api_cart_add(request):
    """API endpoint to add item to cart."""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant_id')
    
    try:
        product = Product.objects.get(id=product_id, status='active')
        cart = Cart.objects.get_or_create_from_session(request)
        
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
            cart.add(product, variant, quantity)
        else:
            cart.add(product, None, quantity)
            
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to cart',
            'cart_total': cart.total_items
        })
    except (Product.DoesNotExist, ProductVariant.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
def api_cart_update(request):
    """API endpoint to update cart item."""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant_id')
    
    try:
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get_or_create_from_session(request)
        
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
            cart.update(product, variant, quantity)
        else:
            cart.update(product, None, quantity)
            
        return JsonResponse({
            'status': 'success',
            'message': 'Cart updated',
            'cart_total': cart.total_items
        })
    except (Product.DoesNotExist, ProductVariant.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
def api_cart_remove(request):
    """API endpoint to remove item from cart."""
    product_id = request.POST.get('product_id')
    
    try:
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get_or_create_from_session(request)
        cart.remove(product)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Product removed from cart',
            'cart_total': cart.total_items
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
