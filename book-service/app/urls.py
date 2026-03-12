from django.urls import path
from .views import BookListCreateView, BookDetailView, BookStockUpdateView, HealthCheckView

urlpatterns = [
    path('books/', BookListCreateView.as_view()),
    path('books/<int:pk>/', BookDetailView.as_view()),
    path('books/<int:pk>/stock/', BookStockUpdateView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
