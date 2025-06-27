from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from user_auth_app.models import UserProfile
from coderr_app.models import Offer, Review

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
