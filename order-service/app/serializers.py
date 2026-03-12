from rest_framework import serializers
from .models import Order, OrderItem, SagaLog


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class SagaLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagaLog
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    saga_logs = SagaLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class CreateOrderSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    shipping_address = serializers.CharField()
    payment_method = serializers.CharField()
    shipping_method = serializers.CharField()
    items = serializers.ListField(
        child=serializers.DictField(), min_length=1
    )
