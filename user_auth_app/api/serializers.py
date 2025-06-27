from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """_summary_
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
        if 'first_name' in validated_data:
            instance.user.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.user.last_name = validated_data['last_name']
        if 'email' in validated_data:
            instance.user.email = validated_data['email']
        instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    
class CustomerProfileSerializer(serializers.ModelSerializer):
    """_summary_
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