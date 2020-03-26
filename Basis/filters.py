import django_filters
from django_filters import NumberFilter, FilterSet

from Einsatztage.models import Buerotag, Fahrtag
from Tour.models import Tour

class TourFilter(django_filters.FilterSet):
	qs = Tour.objects.values('datum__datum__year').distinct()
	year_choices = []
	for item in qs:
		year_choices.append((item['datum__datum__year'],item['datum__datum__year']))
	year = django_filters.ChoiceFilter(choices=year_choices, label='Jahr')
	
	page_choices = (('Touren','Touren'),('Koordinatoren','Koordinatoren'))
	page = django_filters.ChoiceFilter(choices=page_choices, label='Report')

	class Meta:
		model = Tour
		fields = ['page','year']

