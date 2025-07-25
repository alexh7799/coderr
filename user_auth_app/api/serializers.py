from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """
    UserProfileSerializer is a serializer for the UserProfile model.
    Returns:
        _type_: _description_   
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default="")
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default="")
    location = serializers.CharField(allow_blank=True, default="")
    tel = serializers.CharField(allow_blank=True, default="")
    description = serializers.CharField(allow_blank=True, default="")
    working_hours = serializers.CharField(allow_blank=True, default="")
    file = serializers.ImageField(allow_null=True, required=False)
    type = serializers.ChoiceField(choices=[('business', 'business'), ('customer', 'customer')], allow_blank=True, default="")

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'username', 'created_at']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    
class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for customer profiles.
    Args:
        serializers (_type_): _description_
    """
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default="")
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default="")
    file = serializers.ImageField(allow_null=True, required=False)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
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
    type = serializers.ChoiceField(choices=UserProfile.TYPE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', "type"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'error': 'passwords do not match'}, status=400)
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'error': 'This email is already in use'}, status=400)
        return data

    def create(self, validated_data):
        user_type = validated_data.pop('type')
        validated_data.pop('repeated_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(
            user=user,
            type=user_type
        )
        return user