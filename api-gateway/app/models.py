from django.db import models


class GatewayUser(models.Model):
    """User for JWT authentication at the gateway level."""
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=256)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class RequestLog(models.Model):
    """Log all incoming API requests."""
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    status_code = models.IntegerField(null=True)
    user = models.CharField(max_length=150, blank=True, default="anonymous")
    ip_address = models.GenericIPAddressField(null=True)
    response_time_ms = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.path} -> {self.status_code}"


class RateLimitEntry(models.Model):
    """Track rate limiting per IP."""
    ip_address = models.GenericIPAddressField()
    request_count = models.IntegerField(default=0)
    window_start = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ip_address',)

    def __str__(self):
        return f"{self.ip_address}: {self.request_count} requests"
