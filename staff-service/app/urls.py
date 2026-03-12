from django.urls import path
from .views import StaffListCreateView, StaffDetailView, HealthCheckView

urlpatterns = [
    path('staff/', StaffListCreateView.as_view()),
    path('staff/<int:pk>/', StaffDetailView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
