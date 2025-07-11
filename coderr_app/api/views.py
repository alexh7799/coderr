from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from user_auth_app.api.permissions import IsBusinessUser, IsOfferOwner
from rest_framework.filters import OrderingFilter, SearchFilter
from user_auth_app.models import UserProfile
from coderr_app.models import Offer, Review, OfferDetail
from .serializers import OfferDetailSerializer, OfferSerializer

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
    GET: Authentifizierte Benutzer können ein einzelnes OfferDetail sehen
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'