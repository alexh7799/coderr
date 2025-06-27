from rest_framework import generics, status
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser


class UserProfileList(generics.ListCreateAPIView):
    """_summary_
    UserProfileList is a custom view that handles the listing and creation of user profiles.
    Returns:
    _type_: _description_
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """_summary_
    UserProfileDetail is a custom view that handles the retrieval, update, and deletion of user profiles.
    Returns:
        _type_: _description_
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class CheckEmailView(APIView):
    """_summary_
    CheckEmailView is a custom view that checks if an email exists in the database.
    Returns:
        _type_: _description_
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return Response({'error': 'Email parameter is required'}, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            return Response({'email': user.email, 'id': user.id, 'fullname': f"{user.first_name} {user.last_name}"}, content_type='application/json', status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'email': email, 'exists': False}, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)


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
                    'fullname': f"{user.first_name} {user.last_name}"}, content_type='application/json', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(ObtainAuthToken):
    """_summary_
    CustomLoginView is a custom login view that inherits from ObtainAuthToken.
    Returns:
        _type_: _description_
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        modified_data = {'username': email, 'password': password}
        serializer = self.serializer_class(data=modified_data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {'token': token.key, 'user_id': user.id, 'email': user.email,
                    'fullname': user.first_name + ' ' + user.last_name}
            return Response(data, content_type='application/json', status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
