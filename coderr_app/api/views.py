from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from user_auth_app.api.permissions import IsBusinessUser, IsOfferOwner, IsCustomerUser, IsOrderBusinessOwner, IsStaffOrAdmin
from rest_framework.filters import OrderingFilter, SearchFilter
from user_auth_app.models import UserProfile
from coderr_app.models import Offer, OfferDetail, Order, Review
from .serializers import OfferDetailSerializer, OfferSerializer, OrderSerializer
from .paginations import PagePagination

class BaseInfoView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg=models.Avg('rating'))['avg'] or 0
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()
        return Response({
            "review_count": review_count,
            "average_rating": round(average_rating, 1),
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        })


class OfferListView(generics.ListCreateAPIView):
    """
    GET: all offers visible to everyone
    POST: only authenticated Business users can create offers
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = PagePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    filterset_fields = ['creator_id', 'min_price', 'max_delivery_time']
    
    def get_permissions(self):
        """
        GET: Everyone can see the list of offers
        POST: Only authenticated users with Business profile can create offers
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    
class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Everyone can see a single offer
    PATCH/PUT: Only the creator can change their offer
    DELETE: Only the creator can delete their offer
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    lookup_field = 'pk'
    
    def get_permissions(self):
        """
        GET: Everyone can see
        PATCH/PUT/DELETE: Only authenticated creators
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOfferOwner()]
    
    def delete(self, request, *args, **kwargs):
        """
        DELETE: Deletes the offer if the user is the creator
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    
class OfferDetailDetailView(generics.RetrieveAPIView):
    """
    GET: Authenticated users can view a single OfferDetail
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        """
        Filtert Orders basierend auf dem angemeldeten User:
        - Customer sieht nur seine eigenen Orders
        - Business User sieht nur Orders für seine Angebote
        """
        user = self.request.user
        
        if user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=user)
                
                if profile.type == 'customer':
                    # Customer sieht nur seine eigenen Bestellungen
                    return Order.objects.filter(customer=user)
                
                elif profile.type == 'business':
                    # Business User sieht nur Orders für seine Angebote
                    return Order.objects.filter(offer_detail__offer__user=user)
                
            except UserProfile.DoesNotExist:
                return Order.objects.none()
        
        return Order.objects.none()
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsCustomerUser()]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
        
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'pk'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['PATCH', 'PUT']:
            return [IsAuthenticated(), IsBusinessUser(), IsOrderBusinessOwner()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return [IsAuthenticated()]
    
    def patch(self, request, *args, **kwargs):
        """
        PATCH: Nur Status kann geändert werden
        """
        # Validiere dass nur Status geändert wird
        allowed_fields = {'status'}
        if not set(request.data.keys()).issubset(allowed_fields):
            return Response(
                {'error': 'Nur das Feld "status" kann geändert werden.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().patch(request, *args, **kwargs)
    
class OrderCountView(APIView):
    """
    GET: Gibt die Anzahl der laufenden Bestellungen ('in_progress') für einen Business User zurück
    """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)
        try:
            profile = UserProfile.objects.get(user=business_user)
            if profile.type != 'business':
                return Response(
                    {'error': 'User ist kein Business User.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User-Profil nicht gefunden.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        order_count = Order.objects.filter(
            offer_detail__offer__user=business_user,
            status='in_progress'
        ).count()
        
        return Response({
            'order_count': order_count
        }, status=status.HTTP_200_OK)
        

class CompletedOrderCountView(APIView):
    """
    GET: Gibt die Anzahl der abgeschlossenen Bestellungen ('completed') für einen Business User zurück
    """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)
        try:
            profile = UserProfile.objects.get(user=business_user)
            if profile.type != 'business':
                return Response(
                    {'error': 'User ist kein Business User.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User-Profil nicht gefunden.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        completed_order_count = Order.objects.filter(
            offer_detail__offer__user=business_user,
            status='completed'
        ).count()
        
        return Response({
            'completed_order_count': completed_order_count
        }, status=status.HTTP_200_OK)