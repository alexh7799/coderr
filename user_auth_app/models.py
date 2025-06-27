from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    """_summary_
    UserProfile is a model that extends the User model to include additional
    information about the user.
    Returns:
        _type_: _description_
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    file = models.ImageField(upload_to='upload/', blank=True, null=True)
    TYPE_CHOICES = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def fullname(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.user.username
