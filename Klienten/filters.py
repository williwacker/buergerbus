import django_filters
from django.db.models.functions import Substr, Upper

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

    qs = Klienten.objects.annotate(firstchar=Upper(Substr('name', 1, 1))).filter(
        typ='F').values('firstchar').distinct().order_by('firstchar')
    choices = []
    for item in qs:
        choices.append((item['firstchar'], item['firstchar']))
        firstchar = django_filters.ChoiceFilter(choices=choices, label='Name')

    class Meta:
        model = Klienten
        fields = ['firstchar', 'ort', 'bus']


class DienstleisterFilter(django_filters.FilterSet):

    qs = Klienten.objects.annotate(firstchar=Upper(Substr('name', 1, 1))).filter(
        typ='D').values('firstchar').distinct().order_by('firstchar')
    choices = []
    for item in qs:
        choices.append((item['firstchar'], item['firstchar']))
        firstchar = django_filters.ChoiceFilter(choices=choices, label='Name')

    class Meta:
        model = Klienten
        fields = ['firstchar', 'ort', 'kategorie']
