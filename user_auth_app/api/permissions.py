from rest_framework.permissions import BasePermission
from ..models import UserProfile

class IsOwnerProfile(BasePermission):
    """_summary_
    IsOwnerProfile is a custom permission class that checks if the user is the owner of the profile.
    Args:
        BasePermission (_type_): _description_
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    
class IsBusinessUser(BasePermission):
    """
    Erlaubt nur Business-Usern das Erstellen von Angeboten.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            try:
                profile = UserProfile.objects.get(user=request.user)
                return profile.type == 'business'
            except UserProfile.DoesNotExist:
                return False
        return True