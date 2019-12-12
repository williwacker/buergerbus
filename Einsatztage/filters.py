import django_filters

from .models import Buerotag, Fahrtag


class FahrtagFilter(django_filters.FilterSet):
    class Meta:
        model = Fahrtag
        fields = ['team']

class BuerotagFilter(django_filters.FilterSet):
    class Meta:
        model = Buerotag
        fields = ['team']     
