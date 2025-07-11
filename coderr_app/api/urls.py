from django.urls import path
from .views import BaseInfoView, OfferListView, OfferDetailView, OfferDetailDetailView

urlpatterns = [
    path('offers/', OfferListView.as_view(), name="offer-list"),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name="offer-detail"),
    path('offerdetails/<int:pk>/', OfferDetailDetailView.as_view(), name="offer-detail-view"),
    path('orders/', name="order-list"),
    path('orders/<int:pk>/', name="order-detail"),
    path('order-count/<int:pk>/', name="order-count"),
    path('completed-order-count/<int:pk>/', name="completed-order-count"),
    path('reviews/', name="review-list"),
    path('reviews/<int:pk>/', name="review-detail"),
    path('base-info/', BaseInfoView.as_view(), name="base-info"),
]