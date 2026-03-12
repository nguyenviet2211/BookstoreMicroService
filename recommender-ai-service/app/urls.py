from django.urls import path
from .views import RecommendationListView, PopularBooksView, HealthCheckView

urlpatterns = [
    path('recommendations/<int:customer_id>/', RecommendationListView.as_view()),
    path('popular/', PopularBooksView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
