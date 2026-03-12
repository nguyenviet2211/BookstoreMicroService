from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from .serializers import PaymentSerializer


class PaymentListView(APIView):
    def get(self, request):
        payments = Payment.objects.all()
        order_id = request.query_params.get('order_id')
        if order_id:
            payments = payments.filter(order_id=order_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentReserveView(APIView):
    """Called by order-service Saga to reserve payment."""
    def post(self, request):
        order_id = request.data.get('order_id')
        customer_id = request.data.get('customer_id')
        amount = request.data.get('amount')
        method = request.data.get('method')

        if not all([order_id, customer_id, amount, method]):
            return Response(
                {"error": "order_id, customer_id, amount, and method are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Payment.objects.filter(order_id=order_id).exists():
            return Response({"error": "Payment already exists for this order"},
                            status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            method=method,
            status='reserved',
        )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentConfirmView(APIView):
    """Confirm a reserved payment."""
    def post(self, request):
        order_id = request.data.get('order_id')
        try:
            payment = Payment.objects.get(order_id=order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        payment.status = 'confirmed'
        payment.save()
        return Response(PaymentSerializer(payment).data)


class PaymentCancelView(APIView):
    """Called by order-service Saga for compensation."""
    def post(self, request):
        order_id = request.data.get('order_id')
        try:
            payment = Payment.objects.get(order_id=order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        payment.status = 'cancelled'
        payment.save()
        return Response({"message": "Payment cancelled"})


class PaymentDetailView(APIView):
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "pay-service"})
