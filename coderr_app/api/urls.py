from django.urls import path
from .views import BaseInfoView

urlpatterns = [
    path('offers/', name="offer-list"),
    path('offers/<int:pk>/', name="offer-detail"),
    path('offerdetails/<int:pk>/', name="offer-detail-view"),
    path('orders/', name="order-list"),
    path('orders/<int:pk>/', name="order-detail"),
    path('order-count/<int:pk>/', name="order-count"),
    path('completed-order-count/<int:pk>/', name="completed-order-count"),
    path('reviews/', name="review-list"),
    path('reviews/<int:pk>/', name="review-detail"),
    path('base-info/', BaseInfoView.as_view(), name="base-info"),
]