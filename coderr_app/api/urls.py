from django.urls import path
from .views import BaseInfoView, OfferListView, OfferDetailView, OfferDetailDetailView, OrderListView, OrderDetailView, OrderCountView, CompletedOrderCountView, ReviewDetailView, ReviewListView

urlpatterns = [
    path('offers/', OfferListView.as_view(), name="offer-list"),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name="offer-detail"),
    path('offerdetails/<int:pk>/', OfferDetailDetailView.as_view(), name="offer-detail-view"),
    path('orders/', OrderListView.as_view(), name="order-list"),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name="order-detail"),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name="order-count"),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name="completed-order-count"),
    path('reviews/', ReviewListView.as_view(), name="review-list"),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name="review-detail"),
    path('base-info/', BaseInfoView.as_view(), name="base-info"),
]