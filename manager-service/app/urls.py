from django.urls import path
from .views import ManagerListCreateView, ManagerDetailView, ManagerStaffView, HealthCheckView

urlpatterns = [
    path('managers/', ManagerListCreateView.as_view()),
    path('managers/<int:pk>/', ManagerDetailView.as_view()),
    path('managers/<int:pk>/staff/', ManagerStaffView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
