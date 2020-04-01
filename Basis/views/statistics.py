from django import forms, template
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from jet.filters import RelatedFieldAjaxListFilter

from Basis.tables import TourStatisticTable, KoordinatorStatisticTable
from Basis.utils import get_sidebar, url_args
from Basis.views import MyListView
from Basis.filters import *
from Tour.models import Tour
from Einsatztage.models import Fahrtag, Buerotag

register = template.Library()


class StatisticView(MyListView):
	permission_required = 'Tour.view_Tour'
	model = Tour

	def get(self, request, *args, **kwargs):
		if not request.user.is_superuser:
			return render(request, 'Basis/403.html')
		self.object_list = self.get_queryset()
		context = self.get_context_data()
		if 'add' in context:
			del context['add']
		return render(request, self.template_name, context)

	def get_queryset(self):
		page = self.request.GET.get('page', 'Touren')
		year = self.request.GET.get('year')
		sort = self.request.GET.get('sort')
		data = self.request.GET.copy()
		if page == 'Touren':
			qs = Tour.objects.values(
				'datum__datum__year', 'datum__datum__month', 'bus__bus').annotate(
				anzahl=Count("id")).order_by(
				'datum__datum__year', 'datum__datum__month', 'bus__bus')
			if year:
				qs = qs.filter(datum__datum__year=year)
			if sort:
				qs = qs.order_by(sort)
			return TourStatisticTable(qs)
		elif page == 'Koordinatoren':
			qs = Tour.objects.values(
				'datum__datum__year', 'datum__datum__month', 'created_by__last_name', 'created_by__first_name').exclude(
				created_by=None).annotate(
				anzahl=Count('id')).order_by(
				'datum__datum__year', 'datum__datum__month', '-anzahl', 'created_by')
			if year:
				qs = qs.filter(datum__datum__year=year)
			if sort:
				qs = qs.order_by(sort)
			return KoordinatorStatisticTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = "Statistik"
		page = self.request.GET.get('page', 'Touren')
		if page == 'Touren':
			context['table_header'] = 'Anzahl Touren pro Monat und Bus'
			context['filter'] = TourFilter(self.request.GET.copy())
		elif page == 'Koordinatoren':
			context['table_header'] = 'Anzahl gebuchte Touren pro Monat und Koordinator'
			context['filter'] = TourFilter(self.request.GET.copy())
		return context
