import hashlib
import time
import jwt
import requests
import logging
from datetime import datetime, timedelta, timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .models import GatewayUser, RequestLog, RateLimitEntry
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, RequestLogSerializer

logger = logging.getLogger(__name__)


# ==============================
# JWT Helpers
# ==============================

def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_request(request):
    """Extract and validate JWT token from Authorization header."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    payload = decode_token(token)
    if not payload:
        return None
    return payload


# ==============================
# Rate Limiting
# ==============================

def check_rate_limit(ip_address):
    """Returns True if request is allowed, False if rate limited."""
    from django.utils import timezone as tz
    now = tz.now()
    window_start = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)

    entry, created = RateLimitEntry.objects.get_or_create(ip_address=ip_address)
    if not created and entry.window_start < window_start:
        entry.request_count = 0
        entry.window_start = now
    entry.request_count += 1
    entry.save()

    return entry.request_count <= settings.RATE_LIMIT_REQUESTS


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


# ==============================
# Auth Views
# ==============================

class RegisterView(APIView):
    """Register a new user for JWT authentication."""
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_token(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Login and get JWT token."""
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            try:
                user = GatewayUser.objects.get(username=username, password_hash=password_hash, is_active=True)
                token = generate_token(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'token': token,
                })
            except GatewayUser.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifyView(APIView):
    """Verify a JWT token."""
    def post(self, request):
        token = request.data.get('token', '')
        payload = decode_token(token)
        if payload:
            return Response({'valid': True, 'payload': payload})
        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)


# ==============================
# Proxy View (Routes to Backend Services)
# ==============================

class ServiceProxyView(APIView):
    """
    API Gateway proxy: routes requests to backend microservices.
    URL pattern: /api/gateway/<service_name>/<path>/
    Applies: JWT auth, rate limiting, logging.
    """

    # Define which routes are public (no auth required)
    PUBLIC_ROUTES = [
        ('book', 'GET'),
        ('catalog', 'GET'),
        ('comment-rate', 'GET'),
        ('recommender', 'GET'),
        ('customer', 'POST'),  # registration
    ]

    # Define role-based access
    ROLE_ACCESS = {
        'admin': ['staff', 'manager', 'customer', 'catalog', 'book', 'cart',
                   'order', 'ship', 'pay', 'comment-rate', 'recommender'],
        'manager': ['staff', 'catalog', 'book', 'order', 'ship', 'pay', 'comment-rate', 'recommender'],
        'staff': ['catalog', 'book', 'order', 'ship', 'comment-rate', 'recommender'],
        'customer': ['book', 'cart', 'order', 'comment-rate', 'recommender', 'catalog'],
    }

    def _proxy_request(self, request, service_name, path):
        start_time = time.time()
        client_ip = get_client_ip(request)

        # Rate limiting
        if not check_rate_limit(client_ip):
            return Response({'error': 'Rate limit exceeded'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Resolve service URL
        service_url = settings.SERVICE_MAP.get(service_name)
        if not service_url:
            return Response({'error': f'Unknown service: {service_name}'}, status=status.HTTP_404_NOT_FOUND)

        # Check authentication for non-public routes
        is_public = any(
            service_name == s and request.method == m
            for s, m in self.PUBLIC_ROUTES
        )

        user_payload = None
        if not is_public:
            user_payload = get_user_from_request(request)
            if not user_payload:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

            # Role-based access control
            role = user_payload.get('role', 'customer')
            allowed_services = self.ROLE_ACCESS.get(role, [])
            if service_name not in allowed_services:
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Build target URL
        target_url = f"{service_url}/api/{path}"

        # Forward request
        try:
            headers = {'Content-Type': 'application/json'}
            if user_payload:
                headers['X-User-Id'] = str(user_payload.get('user_id', ''))
                headers['X-User-Role'] = user_payload.get('role', '')
                headers['X-Username'] = user_payload.get('username', '')

            method = request.method.lower()
            kwargs = {'headers': headers, 'timeout': 30}

            if method in ('post', 'put', 'patch'):
                kwargs['json'] = request.data

            resp = getattr(requests, method)(target_url, **kwargs)
            response_time = (time.time() - start_time) * 1000

            # Log request
            RequestLog.objects.create(
                method=request.method,
                path=f"/{service_name}/{path}",
                status_code=resp.status_code,
                user=user_payload.get('username', 'anonymous') if user_payload else 'anonymous',
                ip_address=client_ip,
                response_time_ms=response_time,
            )

            try:
                response_data = resp.json()
            except ValueError:
                response_data = {"raw": resp.text}

            return Response(response_data, status=resp.status_code)

        except requests.exceptions.ConnectionError:
            logger.error(f"Service {service_name} unreachable at {service_url}")
            return Response(
                {'error': f'Service {service_name} is unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except requests.exceptions.Timeout:
            return Response(
                {'error': f'Service {service_name} timed out'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )

    def get(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def post(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def put(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def patch(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def delete(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)


# ==============================
# Admin / Monitoring Views
# ==============================

class RequestLogListView(APIView):
    """View request logs (admin only)."""
    def get(self, request):
        user_payload = get_user_from_request(request)
        if not user_payload or user_payload.get('role') != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        logs = RequestLog.objects.order_by('-created_at')[:100]
        serializer = RequestLogSerializer(logs, many=True)
        return Response(serializer.data)


class ServiceHealthView(APIView):
    """Check health of all backend services."""
    def get(self, request):
        health_status = {}
        for name, url in settings.SERVICE_MAP.items():
            try:
                resp = requests.get(f"{url}/api/health/", timeout=5)
                health_status[name] = {
                    'status': 'healthy' if resp.status_code == 200 else 'unhealthy',
                    'status_code': resp.status_code
                }
            except requests.exceptions.RequestException:
                health_status[name] = {'status': 'unreachable'}
        return Response(health_status)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "api-gateway"})
