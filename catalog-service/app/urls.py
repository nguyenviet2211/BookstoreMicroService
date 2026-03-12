from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView, CategoryBooksView, HealthCheckView

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),
    path('categories/<int:pk>/books/', CategoryBooksView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
