from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from products.models import Product, ProductVariant
from ..models import Cart, CartItem
from ..serializers import CartSerializer, CartItemSerializer

class CartDetailView(APIView):
    """
    Get cart details
    """
    def get(self, request):
        cart = Cart.objects.get_or_create_from_session(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartAddView(APIView):
    """
    Add item to cart
    """
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        variant_id = request.data.get('variant_id')
        
        try:
            product = Product.objects.get(id=product_id, status='active')
            cart = Cart.objects.get_or_create_from_session(request)
            
            if variant_id:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                cart.add(product, variant, quantity)
            else:
                cart.add(product, None, quantity)
                
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class CartUpdateView(APIView):
    """
    Update cart item quantity
    """
    def put(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        variant_id = request.data.get('variant_id')
        
        try:
            product = Product.objects.get(id=product_id)
            cart = Cart.objects.get_or_create_from_session(request)
            
            if variant_id:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                cart.update(product, variant, quantity)
            else:
                cart.update(product, None, quantity)
                
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class CartRemoveView(APIView):
    """
    Remove item from cart
    """
    def post(self, request):
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        
        try:
            product = Product.objects.get(id=product_id)
            cart = Cart.objects.get_or_create_from_session(request)
            
            if variant_id:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                cart.remove(product, variant)
            else:
                cart.remove(product)
                
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class CartClearView(APIView):
    """
    Clear all items from cart
    """
    def post(self, request):
        cart = Cart.objects.get_or_create_from_session(request)
        cart.clear()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
