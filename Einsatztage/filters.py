import django_filters

from .models import Buerotag, Fahrtag
from Einsatzmittel.models import Bus, Buero


class FahrtagFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_list = list(self.queryset.order_by('team').values_list('team', flat=True).distinct())
        self.base_filters['team'] = django_filters.ModelChoiceFilter(
            queryset=Bus.objects.filter(id__in=team_list),
            field_name='team', to_field_name='id')

        super(FahrtagFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Fahrtag
        fields = ['team']


class BuerotagFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_list = list(self.queryset.order_by('team').values_list('team', flat=True).distinct())
        self.base_filters['team'] = django_filters.ModelChoiceFilter(
            queryset=Buero.objects.filter(id__in=team_list),
            field_name='team', to_field_name='id')

        super(BuerotagFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Fahrtag
        fields = ['team']

    class Meta:
        model = Buerotag
        fields = ['team']
