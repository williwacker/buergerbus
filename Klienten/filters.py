import django_filters
from django.conf import settings
from django.db.models.functions import Substr, Upper

from .models import Klienten, Orte, Strassen
from Einsatzmittel.models import Bus


class StrassenFilter(django_filters.FilterSet):
    class Meta:
        model = Strassen
        fields = ['ort']


class OrteFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        bus_list = list(self.queryset.order_by('bus').exclude(bus=None).values_list('bus', flat=True).distinct())
        self.base_filters['bus'] = django_filters.ModelChoiceFilter(
            queryset=Bus.objects.filter(id__in=bus_list),
            field_name='bus', to_field_name='id', null_label='nicht gesetzt')

        super(OrteFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Orte
        fields = ['bus']


class FahrgaesteFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        name_choices = list(self.queryset.annotate(
            firstchar=Upper(Substr('name', 1, 1))).order_by(
                'firstchar').values_list('firstchar', 'firstchar').distinct())
        self.base_filters['name'] = django_filters.ChoiceFilter(choices=name_choices, label='Name')

        bus_list = list(self.queryset.order_by('bus').exclude(bus=None).values_list('bus', flat=True).distinct())
        self.base_filters['bus'] = django_filters.ModelChoiceFilter(
            queryset=Bus.objects.filter(id__in=bus_list),
            field_name='bus', to_field_name='id', null_label='nicht gesetzt')

        ort_list = list(self.queryset.order_by('ort').values_list('ort', flat=True).distinct())
        self.base_filters['ort'] = django_filters.ModelChoiceFilter(
            queryset=Orte.objects.filter(id__in=ort_list),
            field_name='ort', to_field_name='id')

        super(FahrgaesteFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Klienten
        fields = ['name', 'ort', 'bus']


class DienstleisterFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        name_choices = list(self.queryset.annotate(
            firstchar=Upper(Substr('name', 1, 1))).order_by(
                'firstchar').values_list('firstchar', 'firstchar').distinct())
        self.base_filters['name'] = django_filters.ChoiceFilter(choices=name_choices, label='Name')

        ort_list = list(self.queryset.order_by('ort').values_list('ort', flat=True).distinct())
        self.base_filters['ort'] = django_filters.ModelChoiceFilter(
            queryset=Orte.objects.filter(id__in=ort_list),
            field_name='ort', to_field_name='id')

        kategorie_choices = list(self.queryset.exclude(kategorie='').exclude(kategorie=None).order_by(
            'kategorie').values_list('kategorie', 'kategorie').distinct())
        self.base_filters['kategorie'] = django_filters.ChoiceFilter(
            choices=kategorie_choices, label='Kategorie', null_label='nicht gesetzt')

        super(DienstleisterFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Klienten
        fields = ['name', 'ort', 'kategorie']
