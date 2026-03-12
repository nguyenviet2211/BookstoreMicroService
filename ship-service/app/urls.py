from django.urls import path
from .views import (
    ShipmentListView, ShipmentReserveView, ShipmentCancelView,
    ShipmentDetailView, HealthCheckView
)

urlpatterns = [
    path('shipments/', ShipmentListView.as_view()),
    path('shipments/reserve/', ShipmentReserveView.as_view()),
    path('shipments/cancel/', ShipmentCancelView.as_view()),
    path('shipments/<int:pk>/', ShipmentDetailView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
