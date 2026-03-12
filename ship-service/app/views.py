from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer
from datetime import date, timedelta


class ShipmentListView(APIView):
    def get(self, request):
        shipments = Shipment.objects.all()
        order_id = request.query_params.get('order_id')
        if order_id:
            shipments = shipments.filter(order_id=order_id)
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)


class ShipmentReserveView(APIView):
    """Called by order-service Saga to reserve shipping."""
    def post(self, request):
        order_id = request.data.get('order_id')
        customer_id = request.data.get('customer_id')
        address = request.data.get('address')
        method = request.data.get('method', 'standard')

        if not all([order_id, customer_id, address]):
            return Response({"error": "order_id, customer_id, and address are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if Shipment.objects.filter(order_id=order_id).exists():
            return Response({"error": "Shipment already exists for this order"},
                            status=status.HTTP_400_BAD_REQUEST)

        delivery_days = {'standard': 7, 'express': 3, 'overnight': 1}
        estimated = date.today() + timedelta(days=delivery_days.get(method, 7))

        shipment = Shipment.objects.create(
            order_id=order_id,
            customer_id=customer_id,
            address=address,
            method=method,
            status='reserved',
            estimated_delivery=estimated,
        )
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShipmentCancelView(APIView):
    """Called by order-service Saga for compensation."""
    def post(self, request):
        order_id = request.data.get('order_id')
        try:
            shipment = Shipment.objects.get(order_id=order_id)
        except Shipment.DoesNotExist:
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        shipment.status = 'cancelled'
        shipment.save()
        return Response({"message": "Shipment cancelled"})


class ShipmentDetailView(APIView):
    def get(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk)
        except Shipment.DoesNotExist:
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk)
        except Shipment.DoesNotExist:
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status')
        if new_status:
            shipment.status = new_status
            shipment.save()
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "ship-service"})
