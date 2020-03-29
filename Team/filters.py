import django_filters

from .models import Fahrer, Koordinator


class FahrerFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_qs = self.queryset.exclude(team=None).values('team', 'team__bus').distinct().order_by('team')
        team_choices = []
        for item in team_qs:
            team_choices.append((item['team'], item['team__bus']))
        self.base_filters['team'] = django_filters.ChoiceFilter(choices=team_choices, label='Team')

        super(FahrerFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Fahrer
        fields = ['team']


class KoordinatorFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_qs = self.queryset.exclude(team=None).values('team', 'team__buero').distinct().order_by('team')
        team_choices = []
        for item in team_qs:
            team_choices.append((item['team'], item['team__buero']))
        self.base_filters['team'] = django_filters.ChoiceFilter(choices=team_choices, label='Team')

        super(KoordinatorFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Koordinator
        fields = ['team']
