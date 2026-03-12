from django.db import models
import uuid


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reserved', 'Reserved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    METHOD_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('overnight', 'Overnight'),
    ]

    order_id = models.IntegerField(unique=True)
    customer_id = models.IntegerField()
    address = models.TextField()
    method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='standard')
    tracking_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"TRK-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipment for Order #{self.order_id} - {self.status}"
