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
    allows only Business-User to create a profile.
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
    allows only the owner of the offer to perform actions on it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    
    
class IsCustomerUser(BasePermission):
    """
    allows only Customer-User to create orders.
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
    allows only the business user of the offer to modify the order.
    """
    def has_object_permission(self, request, view, obj):
        return obj.offer_detail.offer.user == request.user

class IsStaffOrAdmin(BasePermission):
    """
    allows only Staff or Admin-User.
    """
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser
    
    
class IsReviewOwner(BasePermission):
    """
    allows only the creator of the review to modify/delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user