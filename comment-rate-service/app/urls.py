from django.urls import path
from .views import (
    ReviewListCreateView, ReviewDetailView,
    BookAverageRatingView, HealthCheckView
)

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view()),
    path('reviews/<int:pk>/', ReviewDetailView.as_view()),
    path('reviews/book/<int:book_id>/average/', BookAverageRatingView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
