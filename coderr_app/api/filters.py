import django_filters
from coderr_app.models import Offer

class OfferFilter(django_filters.FilterSet):
    creator_id = django_filters.NumberFilter(field_name='user__id')
    max_delivery_time = django_filters.NumberFilter(field_name='min_delivery_time', lookup_expr='lte')
    
    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']