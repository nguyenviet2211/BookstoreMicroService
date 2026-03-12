from django.urls import path
from .views import CustomerListCreateView, CustomerDetailView, HealthCheckView

urlpatterns = [
    path('customers/', CustomerListCreateView.as_view()),
    path('customers/<int:pk>/', CustomerDetailView.as_view()),
    path('health/', HealthCheckView.as_view()),
]