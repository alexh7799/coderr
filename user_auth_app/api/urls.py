from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegistrationView, CustomLoginView, CustomerProfileList

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('profiles/business/', UserProfileList.as_view(), name='userprofile-list-business'),
    path('profiles/customers/', CustomerProfileList.as_view(), name='userprofile-list-customers'),
]
