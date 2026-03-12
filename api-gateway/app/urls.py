from django.urls import path, re_path
from .views import (
    RegisterView,
    LoginView,
    TokenVerifyView,
    ServiceProxyView,
    RequestLogListView,
    ServiceHealthView,
    HealthCheckView,
)

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/verify/', TokenVerifyView.as_view()),

    # Monitoring
    path('health/', HealthCheckView.as_view()),
    path('services/health/', ServiceHealthView.as_view()),
    path('logs/', RequestLogListView.as_view()),

    # Gateway proxy - routes to backend services
    re_path(r'^gateway/(?P<service_name>[\w-]+)/(?P<path>.*)$', ServiceProxyView.as_view()),
]
