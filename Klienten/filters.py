import django_filters
from django.conf import settings
from django.db.models.functions import Substr, Upper

from .models import Klienten, Orte, Strassen


class StrassenFilter(django_filters.FilterSet):
    class Meta:
        model = Strassen
        fields = ['ort']


class OrteFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        bus_qs = self.queryset.values('bus', 'bus__bus').distinct().order_by('bus')
        bus_choices = []
        for item in bus_qs:
            if not item['bus']:
                continue
            bus_choices.append((item['bus'], item['bus__bus']))
        self.base_filters['bus'] = django_filters.ChoiceFilter(
            choices=bus_choices, label='Bus', null_label='nicht gesetzt')

        super(OrteFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Orte
        fields = ['bus']


class FahrgaesteFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        bus_qs = self.queryset.values('bus', 'bus__bus').distinct().order_by('bus')
        bus_choices = []
        for item in bus_qs:
            if not item['bus']:
                continue
            bus_choices.append((item['bus'], item['bus__bus']))
        self.base_filters['bus'] = django_filters.ChoiceFilter(
            choices=bus_choices, label='Bus', null_label='nicht gesetzt')

        ort_qs = self.queryset.values('ort', 'ort__ort').distinct().order_by('ort')
        ort_choices = []
        for item in ort_qs:
            ort_choices.append((item['ort'], item['ort__ort']))
        self.base_filters['ort'] = django_filters.ChoiceFilter(choices=ort_choices, label='Ort')

        klienten_qs = self.queryset.annotate(firstchar=Upper(Substr('name', 1, 1))).values(
            'firstchar').distinct().order_by('firstchar')
        klienten_choices = []
        for item in klienten_qs:
            klienten_choices.append((item['firstchar'], item['firstchar']))
        self.base_filters['name'] = django_filters.ChoiceFilter(choices=klienten_choices, label='Name')

        super(FahrgaesteFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Klienten
        fields = ['name', 'ort', 'bus']


class DienstleisterFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        ort_qs = self.queryset.values('ort', 'ort__ort').distinct().order_by('ort')
        ort_choices = []
        for item in ort_qs:
            ort_choices.append((item['ort'], item['ort__ort']))
        self.base_filters['ort'] = django_filters.ChoiceFilter(choices=ort_choices, label='Ort')

        kategorie_qs = self.queryset.values('kategorie', 'kategorie').distinct().order_by('kategorie')
        kategorie_choices = []
        for item in kategorie_qs:
            if not item['kategorie']:
                continue
            kategorie_choices.append((item['kategorie'], item['kategorie']))
        self.base_filters['kategorie'] = django_filters.ChoiceFilter(
            choices=kategorie_choices, label='Kategorie', null_label='nicht gesetzt')

        klienten_qs = self.queryset.annotate(firstchar=Upper(Substr('name', 1, 1))).values(
            'firstchar').distinct().order_by('firstchar')
        klienten_choices = []
        for item in klienten_qs:
            klienten_choices.append((item['firstchar'], item['firstchar']))
        self.base_filters['name'] = django_filters.ChoiceFilter(choices=klienten_choices, label='Name')

        super(DienstleisterFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Klienten
        fields = ['name', 'ort', 'kategorie']
