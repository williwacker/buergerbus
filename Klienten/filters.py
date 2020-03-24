import django_filters

from .models import Klienten, Orte, Strassen


class StrassenFilter(django_filters.FilterSet):
    class Meta:
        model = Strassen
        fields = ['ort']


class OrteFilter(django_filters.FilterSet):
    class Meta:
        model = Orte
        fields = ['bus']


class FahrgaesteFilter(django_filters.FilterSet):
    class Meta:
        model = Klienten
        fields = ['ort', 'bus']


class DienstleisterFilter(django_filters.FilterSet):
    class Meta:
        model = Klienten
        fields = ['ort', 'kategorie']
