from io import BytesIO
from .utils import render_to_pdf
from django.template.loader import get_template
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django import forms

from .models import Fahrtag
from Tour.models import Tour
from Einsatzmittel.models import Bus

def get_sidebar():
	return [{'name':'Admin','value':'/admin/'},{'name':'Einsatztage','value':'/Einsatztage/'},{'name':'Tour','value':'/Tour/'}]

class TourView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	template_name = 'Einsatztage/tour.html'
	context_object_name = 'fahrtag_liste'
	ordering = ['uhrzeit']

	def get_queryset(self):
		return Fahrtag.objects.filter(pk=self.kwargs['id']).first()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['tour_liste'] = Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id'])
		context['sidebar_liste'] = get_sidebar()
		return context


class GeneratePDF(LoginRequiredMixin, View):
	login_url = settings.LOGIN_URL
	def get(self, request, id):
		fahrtag_liste = Fahrtag.objects.filter(pk=id).first()
		tour_liste = Tour.objects.order_by('uhrzeit').filter(datum=id)
		context = {'fahrtag_liste':fahrtag_liste,'tour_liste':tour_liste,'skip_nav':1}
		pdf = render_to_pdf('Einsatztage/tour_as_pdf.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "Buergerbus_Tour_Bus_%s_%s.pdf" % (fahrtag_liste.team_id, fahrtag_liste.datum)
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Kein Dokument vorhanden")	

class FahrtageView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	queryset = Fahrtag.objects.order_by('team','datum').filter(archiv=False)
	template_name = 'Einsatztage/index.html'
	context_object_name = 'einsatz_liste'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar()
		return context

class FahrtageDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	template_name = 'Einsatztage/detail.html'
	context_object_name = 'fahrer'
	

	def get_queryset(self):
		return Fahrtag.objects.filter(pk=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar()
		return context



