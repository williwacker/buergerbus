import django_filters

from .models import Buerotag, Fahrtag


class FahrtagFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_qs = self.queryset.exclude(team=None).values('team', 'team__bus').distinct().order_by('team')
        team_choices = []
        for item in team_qs:
            team_choices.append((item['team'], item['team__bus']))
        self.base_filters['team'] = django_filters.ChoiceFilter(choices=team_choices, label='Team')

        super(FahrtagFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Fahrtag
        fields = ['team']


class BuerotagFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')

        team_qs = self.queryset.exclude(team=None).values('team', 'team__buero').distinct().order_by('team')
        team_choices = []
        for item in team_qs:
            team_choices.append((item['team'], item['team__buero']))
        self.base_filters['team'] = django_filters.ChoiceFilter(choices=team_choices, label='Team')

        super(BuerotagFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Fahrtag
        fields = ['team']

    class Meta:
        model = Buerotag
        fields = ['team']
