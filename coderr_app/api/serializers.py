from rest_framework import serializers

class OfferSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    
    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }
    
    def get_details(self, obj):
        # Hier die verknüpften Detail-Objekte holen
        return [{"id": detail.id, "url": f"/offerdetails/{detail.id}/"} for detail in obj.details.all()]