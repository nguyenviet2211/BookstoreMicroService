from django.urls import path
from .views import (
    CartListCreateView, CartDetailView,
    CartItemAddView, CartItemUpdateDeleteView,
    HealthCheckView
)

urlpatterns = [
    path('carts/', CartListCreateView.as_view()),
    path('carts/<int:customer_id>/', CartDetailView.as_view()),
    path('carts/<int:customer_id>/items/', CartItemAddView.as_view()),
    path('carts/<int:customer_id>/items/<int:item_id>/', CartItemUpdateDeleteView.as_view()),
    path('health/', HealthCheckView.as_view()),
]
