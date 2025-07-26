from django.contrib.auth.models import User
from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail, Order, Review
from user_auth_app.models import UserProfile


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the OfferDetail model.
    Args:
        serializers (_type_): _description_
    """
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']
        

class OfferSerializer(serializers.ModelSerializer):
    """
    OfferSerializer is a serializer for the Offer model.
    It includes fields for the offer details and user information.
    """
    user_details = serializers.SerializerMethodField()
    details = OfferDetailSerializer(many=True, required=False) 
    
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        read_only_fields = ['user', 'created_at', 'updated_at', 'min_price', 'min_delivery_time']
        
    def _create_detail_urls(self, instance, request, absolute=True):
        """create URLs for Details"""
        if absolute:
            return [
                {
                    "id": detail.id, 
                    "url": request.build_absolute_uri(f"/api/offerdetails/{detail.id}/")
                } 
                for detail in instance.details.all()
            ]
        else:
            return [
                {"id": detail.id, "url": f"/offerdetails/{detail.id}/"} 
                for detail in instance.details.all()
            ]

    def _is_detail_view(self, request):
        """Check if the request is for a detail view."""
        try:
            return '/offers/' in request.path and request.path.split('/')[-2].isdigit()
        except (AttributeError, IndexError):
            return False

    def _remove_post_patch_fields(self, data):
        """Remove fields that should not be included in POST/PATCH responses."""
        fields_to_remove = [
            'user', 'created_at', 'updated_at', 
            'min_price', 'min_delivery_time', 'user_details'
        ]
        for field in fields_to_remove:
            data.pop(field, None)

    def _handle_get_response(self, instance, data, request):
        """Handle GET response to include detail URLs."""
        is_detail_view = self._is_detail_view(request)
        if is_detail_view:
            data['details'] = self._create_detail_urls(instance, request, absolute=True)
            data.pop('user_details', None)
        else:
            data['details'] = self._create_detail_urls(instance, request, absolute=False)

    def to_representation(self, instance):
        """Adjust the response based on the request method"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        if not request:
            return data
        if request.method in ['POST', 'PATCH']:
            self._remove_post_patch_fields(data)
        elif request.method == 'GET':
            self._handle_get_response(instance, data, request)
        return data
        
    
    def get_user_details(self, obj):
        """Get user details for the offer."""
        request = self.context.get('request')
        if not request or request.method != 'GET':
            return None
        try:
            is_detail_view = '/offers/' in request.path and request.path.split('/')[-2].isdigit()
        except (AttributeError, IndexError):
            is_detail_view = False
        if not is_detail_view:
            return {
                "first_name": obj.user.first_name,
                "last_name": obj.user.last_name,
                "username": obj.user.username
            }
        return None
    
    def validate_details(self, value):
        """Validate the details field to ensure it contains exactly 3 items."""
        if self.instance is not None:
            return value
        if len(value) != 3:
            raise serializers.ValidationError("must provide exactly 3 details.", status_code=403)
        offer_types = [detail['offer_type'] for detail in value]
        required_types = ['basic', 'standard', 'premium']
        if set(offer_types) != set(required_types):
            raise serializers.ValidationError("Details must include the types 'basic', 'standard', and 'premium'.", status_code=403)
        return value
    
    def create(self, validated_data):
        """Create a new Offer instance with its details."""
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        details = offer.details.all()
        if details:
            offer.min_price = min(detail.price for detail in details)
            offer.min_delivery_time = min(detail.delivery_time_in_days for detail in details)
            offer.save()
        return offer
    
    def _update_offer_fields(self, instance, validated_data):
        """Update the main fields of the offer"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def _update_existing_detail(self, existing_detail, detail_data):
        """Update an existing OfferDetail"""
        for attr, value in detail_data.items():
            setattr(existing_detail, attr, value)
        existing_detail.save()

    def _create_new_detail(self, instance, detail_data):
        """create a new OfferDetail"""
        OfferDetail.objects.create(offer=instance, **detail_data)

    def _update_min_values(self, instance):
        """Update min_price and min_delivery_time"""
        details = instance.details.all()
        if details:
            instance.min_price = min(detail.price for detail in details)
            instance.min_delivery_time = min(detail.delivery_time_in_days for detail in details)
            instance.save()

    def _update_offer_details(self, instance, details_data):
        """Update all OfferDetails"""
        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')
            existing_detail = instance.details.filter(offer_type=offer_type).first()
            if existing_detail:
                self._update_existing_detail(existing_detail, detail_data)
            else:
                self._create_new_detail(instance, detail_data)

    def update(self, instance, validated_data):
        """Update an existing Offer instance."""
        details_data = validated_data.pop('details', None)
        self._update_offer_fields(instance, validated_data)
        if details_data is not None:
            self._update_offer_details(instance, details_data)
            self._update_min_values(instance)
        return instance
         

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    Args:
        serializers (_type_): _description_
    Raises:
        serializers.ValidationError: _description_
    Returns:
        _type_: _description_
    """
    offer_detail_id = serializers.IntegerField(write_only=True)
    customer_user = serializers.IntegerField(source='customer.id', read_only=True)
    business_user = serializers.IntegerField(source='offer_detail.offer.user.id', read_only=True)
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.ListField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)
    status = serializers.ChoiceField(
        choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        required=False,
        default='in_progress'
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions', 
            'delivery_time_in_days', 'price', 'features', 'offer_type', 
            'status', 'created_at', 'updated_at', 'offer_detail_id'
        ]
        read_only_fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'created_at', 'updated_at'
        ]
    
    def validate_offer_detail_id(self, value):
        try:
            OfferDetail.objects.get(id=value) 
            return value
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("Offer not found.")
    
    def create(self, validated_data):
        if 'offer_detail_id' not in validated_data:
            raise serializers.ValidationError("offer id is required.")
        offer_detail_id = validated_data['offer_detail_id']
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        return Order.objects.create(
            customer=self.context['request'].user,
            offer_detail=offer_detail,
            status=validated_data.get('status', 'in_progress')
        )
        
    def update(self, instance, validated_data):
        validated_data.pop('offer_detail_id', None)
        if 'status' in validated_data:
            instance.status = validated_data['status']
            instance.save()
        return instance
    
        

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer für das Review-Modell.
    Args:
        serializers (_type_): _description_
    Raises:
        serializers.ValidationError: _description_
    Returns:
        _type_: _description_
    """
    business_user = serializers.IntegerField(write_only=True)
    business_user_id = serializers.IntegerField(source='business_user.id', read_only=True)
    reviewer = serializers.IntegerField(source='reviewer.id', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'business_user_id', 'reviewer', 
            'rating', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'business_user_id', 'reviewer', 'created_at', 'updated_at']
    
    def validate_business_user(self, value):
        try:
            user = User.objects.get(id=value)
            profile = UserProfile.objects.get(user=user)
            if profile.type != 'business':
                raise serializers.ValidationError("User is not a business user.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Business User not found.")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Business User not found.")
        return value
    
    def validate(self, data):
        request = self.context['request']
        business_user_id = data.get('business_user')
        if self.instance is None and business_user_id:
            existing_review = Review.objects.filter(
                business_user_id=business_user_id,
                reviewer=request.user
            ).first()
            if existing_review:
                raise serializers.ValidationError("You have already submitted a review for this business user.")
        return data
    
    def create(self, validated_data):
        business_user_id = validated_data.pop('business_user')
        business_user = User.objects.get(id=business_user_id)
        return Review.objects.create(
            business_user=business_user,
            reviewer=self.context['request'].user,
            rating=validated_data['rating'],
            description=validated_data['description']
        )
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('business_user', None)
        if 'business_user_id' in data:
            data['business_user'] = data.pop('business_user_id')
        return data
    
    def update(self, instance, validated_data):
        validated_data.pop('business_user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance