from rest_framework.permissions import BasePermission

class IsOwnerProfile(BasePermission):
    """_summary_
    IsOwnerProfile is a custom permission class that checks if the user is the owner of the profile.
    Args:
        BasePermission (_type_): _description_
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user