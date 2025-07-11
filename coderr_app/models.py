from django.db import models
from django.contrib.auth.models import User

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_delivery_time = models.PositiveIntegerField()  # in Tagen
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=200)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()  # Umbenennen von delivery_time
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)  # Für Array von Features
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.offer.title} - {self.title}"
