import django_filters
from .models import Tour
from Einsatztage.models import Fahrtag

class TourFilter(django_filters.FilterSet):

    class Meta:
        model = Tour
        fields = ['datum','bus']