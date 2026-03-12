from django.urls import path
from .views import OrderListCreateView, OrderDetailView, HealthCheckView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
