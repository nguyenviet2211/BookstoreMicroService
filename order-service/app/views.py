from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from .saga import OrderSagaOrchestrator

import logging

logger = logging.getLogger(__name__)


class OrderListCreateView(APIView):
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        orders = Order.objects.all()
        if customer_id:
            orders = orders.filter(customer_id=customer_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create order and execute Saga orchestration."""
        ser = CreateOrderSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        data = ser.validated_data

        # Create order
        order = Order.objects.create(
            customer_id=data['customer_id'],
            shipping_address=data['shipping_address'],
            payment_method=data['payment_method'],
            shipping_method=data['shipping_method'],
            status='pending',
        )

        # Create order items
        total = Decimal('0')
        for item_data in data['items']:
            book_id = item_data.get('book_id')
            quantity = item_data.get('quantity', 1)
            price = Decimal(str(item_data.get('price', 0)))
            OrderItem.objects.create(
                order=order, book_id=book_id,
                quantity=quantity, price=price
            )
            total += price * quantity

        order.total_amount = total
        order.save()

        # Execute Saga
        saga = OrderSagaOrchestrator(order)
        success = saga.execute()

        order.refresh_from_db()
        serializer = OrderSerializer(order)

        if success:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Order creation failed - saga compensated", "order": serializer.data},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


class OrderDetailView(APIView):
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Update order status."""
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status')
        if new_status:
            order.status = new_status
            order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "order-service"})
