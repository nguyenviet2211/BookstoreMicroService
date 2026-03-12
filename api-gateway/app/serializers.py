from rest_framework import serializers
from .models import GatewayUser, RequestLog


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = GatewayUser
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        import hashlib
        password = validated_data.pop('password')
        validated_data['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
        return GatewayUser.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatewayUser
        fields = ['id', 'username', 'email', 'role', 'is_active', 'created_at']


class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = '__all__'
