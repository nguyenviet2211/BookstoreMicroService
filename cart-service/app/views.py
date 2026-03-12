from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

import requests
import logging

logger = logging.getLogger(__name__)

BOOK_SERVICE_URL = 'http://book-service:8005'


class CartListCreateView(APIView):
    """Create cart (called by customer-service on registration)."""
    def get(self, request):
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({"error": "customer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if Cart.objects.filter(customer_id=customer_id).exists():
            return Response({"error": "Cart already exists for this customer"}, status=status.HTTP_400_BAD_REQUEST)
        cart = Cart.objects.create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartDetailView(APIView):
    """View cart by customer_id."""
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request, customer_id):
        """Clear all items in cart."""
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)


class CartItemAddView(APIView):
    """Customer adds book to cart."""
    def post(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        book_id = request.data.get('book_id')
        quantity = request.data.get('quantity', 1)

        if not book_id:
            return Response({"error": "book_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify book exists via book-service
        try:
            response = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=5)
            if response.status_code != 200:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Book service unavailable: {e}")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, book_id=book_id,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemUpdateDeleteView(APIView):
    """Update or remove item from cart."""
    def put(self, request, customer_id, item_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            item = CartItem.objects.get(pk=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is not None:
            item.quantity = int(quantity)
            item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    def delete(self, request, customer_id, item_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            item = CartItem.objects.get(pk=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "cart-service"})
