from django.db import models
from django.contrib.auth.models import User

class Offer(models.Model):
    """
    Offer model for managing offers.
    Args:
        models (_type_): _description_
    Returns:
        _type_: _description_
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='offers/', blank=True, default="")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_delivery_time = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class OfferDetail(models.Model):
    """
    OfferDetail model for managing offer details.
    Args:
        models (_type_): _description_
    Returns:
        _type_: _description_
    """
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=200)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.offer.title} - {self.title}"


class Order(models.Model):
    """
    Order model for managing customer orders.
    Args:
        models (_type_): _description_
    Returns:
        _type_: _description_
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.offer_detail.title}"
    
    
class Review(models.Model):
    """
    Review model for user feedback on offers.
    Args:
        models (_type_): _description_
    Returns:
        _type_: _description_
    """
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username}"
    