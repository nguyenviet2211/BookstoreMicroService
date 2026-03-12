from django.db import models


class Manager(models.Model):
    DEPARTMENT_CHOICES = [
        ('sales', 'Sales'),
        ('inventory', 'Inventory'),
        ('operations', 'Operations'),
        ('hr', 'Human Resources'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.department}"
