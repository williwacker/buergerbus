import django_filters
from django_filters import NumberFilter, FilterSet

from Einsatztage.models import Buerotag, Fahrtag
from Tour.models import Tour


class TourFilter(django_filters.FilterSet):
    year_list = list(Tour.objects.order_by('datum__datum__year').values_list('datum__datum__year', 'datum__datum__year').distinct())
    year = django_filters.ChoiceFilter(choices=year_list, label='Jahr')

    page_choices = (
        ('Touren', 'Touren'),
        ('Koordinatoren', 'Koordinatoren')
    )
    page = django_filters.ChoiceFilter(choices=page_choices, label='Report')

    class Meta:
        model = Tour
        fields = ['page', 'year']
