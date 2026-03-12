from django.urls import path
from .views import (
    PaymentListView, PaymentReserveView, PaymentConfirmView,
    PaymentCancelView, PaymentDetailView, HealthCheckView
)

urlpatterns = [
    path('payments/', PaymentListView.as_view()),
    path('payments/reserve/', PaymentReserveView.as_view()),
    path('payments/confirm/', PaymentConfirmView.as_view()),
    path('payments/cancel/', PaymentCancelView.as_view()),
    path('payments/<int:pk>/', PaymentDetailView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
