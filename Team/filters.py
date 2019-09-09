import django_filters
from .models import Koordinator, Fahrer

class FahrerFilter(django_filters.FilterSet):
    class Meta:
        model = Fahrer
        fields = ['team']

class KoordinatorFilter(django_filters.FilterSet):
    class Meta:
        model = Koordinator
        fields = ['team']          