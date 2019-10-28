import django_filters
from .models import Tour

class TourFilter(django_filters.FilterSet):

    class Meta:
        model = Tour
        fields = ['datum','bus']