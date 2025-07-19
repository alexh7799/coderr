from rest_framework.permissions import BasePermission
from ..models import UserProfile

class IsOwnerProfile(BasePermission):
    """_summary_
    IsOwnerProfile is a custom permission class that checks if the user is the owner of the profile.
    Args:
        BasePermission (_type_): _description_
    """
    def has_permission(self, request, view):
        obj = view.get_object()
        return request.user == obj.user


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
    
class IsOfferOwner(BasePermission):
    """
    Erlaubt nur dem Ersteller des Angebots Änderungen.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    
    
class IsCustomerUser(BasePermission):
    """
    Erlaubt nur Customer-Usern das Erstellen von Bestellungen.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            try:
                profile = UserProfile.objects.get(user=request.user)
                return profile.type == 'customer'
            except UserProfile.DoesNotExist:
                return False
        return True
    
class IsOrderBusinessOwner(BasePermission):
    """
    Erlaubt nur dem Business-User des Angebots, die Order zu ändern.
    """
    def has_object_permission(self, request, view, obj):
        # Nur der Business-User, der das Angebot erstellt hat
        return obj.offer_detail.offer.user == request.user

class IsStaffOrAdmin(BasePermission):
    """
    Erlaubt nur Staff oder Admin-Usern.
    """
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser