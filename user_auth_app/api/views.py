from rest_framework import generics, status
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer, CustomerProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from user_auth_app.api.permissions import IsOwnerProfile


class UserProfileList(generics.ListCreateAPIView):
    """_summary_
    UserProfileList is a custom view that handles the listing and creation of user profiles.
    Returns:
    _type_: _description_
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='business')
    
    
class CustomerProfileList(generics.ListAPIView):
    """_summary_
    CustomerProfileList is a custom view that handles the listing of customer profiles.
    Args:
        generics (_type_): _description_
    """
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """_summary_
    UserProfileDetail is a custom view that handles the retrieval, update, and deletion of user profiles.
    Returns:
        _type_: _description_
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerProfile]
    
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except UserProfile.DoesNotExist:
            return Response({'detail': 'The Profile was not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated:
            return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except UserProfile.DoesNotExist:
            return Response({'detail': 'The Profile was not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated:
            return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
        if instance.user != request.user:
            return Response({'detail': 'Authenticated user is not the owner of the profile.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    """_summary_
    RegistrationView is a custom view that handles user registration.
    Returns:
        _type_: _description_
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id, 'email': user.email,
                    'username': user.username}, content_type='application/json', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(ObtainAuthToken):
    """_summary_
    CustomLoginView is a custom login view that inherits from ObtainAuthToken.
    Returns:
        _type_: _description_
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        modified_data = {'username': username, 'password': password}
        serializer = self.serializer_class(data=modified_data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {'token': token.key, 'user_id': user.id, 'email': user.email, 'username': user.username}
            return Response(data, content_type='application/json', status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
