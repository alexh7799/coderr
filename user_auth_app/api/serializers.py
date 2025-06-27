from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """_summary_
    UserProfileSerializer is a serializer for the UserProfile model.
    Returns:
        _type_: _description_   
    """
    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'location']


class UserSerializer(serializers.ModelSerializer):
    """_summary_
    UserSerializer is a serializer for the User model.
    Returns:
        _type_: _description_
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class RegistrationSerializer(serializers.ModelSerializer):
    """_summary_
    RegistrationSerializer is a serializer for user registration.
    Returns:
        _type_: _description_
    """
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_fullname(self, value):
        if len(value.split()) < 2:
            raise serializers.ValidationError(
                "your fullname must contain at least a first name and a last name")
        return value
    
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'error': 'passwords do not match'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'error': 'This email is already in use'})
        return data

    def create(self, validated_data):
        fullname_parts = validated_data['fullname'].split(' ')
        firstname = fullname_parts[0]
        lastname = ' '.join(fullname_parts[1:])
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=firstname,
            last_name=lastname
        )
        return user