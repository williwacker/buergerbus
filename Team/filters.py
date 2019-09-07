import django_filters
from .models import Buerokraft, Fahrer

class FahrerFilter(django_filters.FilterSet):
    class Meta:
        model = Fahrer
        fields = ['team']

class BuerokraftFilter(django_filters.FilterSet):
    class Meta:
        model = Buerokraft
        fields = ['team']          