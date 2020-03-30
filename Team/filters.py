import django_filters

from .models import Fahrer, Koordinator
from Einsatzmittel.models import Bus, Buero


class FahrerFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_list = list(self.queryset.order_by('team').values_list('team', flat=True).distinct())
        self.base_filters['team'] = django_filters.ModelChoiceFilter(
            queryset=Bus.objects.filter(id__in=team_list),
            field_name='team', to_field_name='id')

        super(FahrerFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Fahrer
        fields = ['team']


class KoordinatorFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_list = list(self.queryset.order_by('team').values_list('team', flat=True).distinct())
        self.base_filters['team'] = django_filters.ModelChoiceFilter(
            queryset=Buero.objects.filter(id__in=team_list),
            field_name='team', to_field_name='id')

        super(KoordinatorFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Koordinator
        fields = ['team']
