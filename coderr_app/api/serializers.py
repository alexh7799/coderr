from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail

class OfferSerializer(serializers.ModelSerializer):
    """_summary_
    OfferSerializer is a serializer for the Offer model.
    It includes fields for the offer details and user information.
    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    user_details = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details', 'details']
    
    
    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }
    
    def get_details(self, obj):
        return [{"id": detail.id, "url": f"/offerdetails/{detail.id}/"} for detail in obj.details.all()]
    
    
class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
    
    
# class OfferSerializer(serializers.ModelSerializer):
#     details = OfferDetailSerializer(many=True)
    
#     class Meta:
#         model = Offer
#         fields = ['id', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']
#         read_only_fields = ['created_at', 'updated_at', 'min_price', 'min_delivery_time']
    
#     def update(self, instance, validated_data):
#         details_data = validated_data.pop('details', None)
        
#         # Offer-Felder aktualisieren
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
        
#         # Details aktualisieren falls vorhanden
#         if details_data:
#             # Bestehende Details aktualisieren oder neue erstellen
#             existing_details = {detail.id: detail for detail in instance.details.all()}
            
#             for detail_data in details_data:
#                 if 'id' in detail_data:
#                     # Update existing detail
#                     detail_id = detail_data.pop('id')
#                     if detail_id in existing_details:
#                         detail = existing_details[detail_id]
#                         for attr, value in detail_data.items():
#                             setattr(detail, attr, value)
#                         detail.save()
#                 else:
#                     # Create new detail
#                     OfferDetail.objects.create(offer=instance, **detail_data)
            
#             # Min-Werte neu berechnen
#             details = instance.details.all()
#             instance.min_price = min(detail.price for detail in details)
#             instance.min_delivery_time = min(detail.delivery_time_in_days for detail in details)
        
#         instance.save()
#         return instance