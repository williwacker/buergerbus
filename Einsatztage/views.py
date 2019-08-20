from Basis.utils import render_to_pdf
from django.template.loader import get_template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django import forms

from .models import Fahrtag
from .utils import FahrtageSchreiben
from .forms import FahrtagChgForm
from Tour.models import Tour
from Team.models import Fahrer, Buerokraft
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list, get_buero_list
from Basis.utils import get_sidebar

class MyListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL

class MyDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL

class TourView(MyListView):
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

class FahrtageView(MyListView):
	template_name = 'Einsatztage/fahrer.html'
	context_object_name = 'einsatz_liste'

	def get_queryset(self):
		FahrtageSchreiben()
		return Fahrtag.objects.order_by('team','datum').filter(archiv=False, team__in=get_bus_list(self.request))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrtage"
		return context

class FahrtageDetailView(MyDetailView):
	form_class = FahrtagChgForm
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'
	context_object_name = 'fahrer'
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrereinsatz ändern"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(instance=Fahrtag.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
		if form.is_valid():
			post = request.POST.dict()
			fahrtag = Fahrtag.objects.get(pk=kwargs['pk'])
			if post['fahrer_vormittag'] != "":
				fahrtag.fahrer_vormittag=Fahrer.objects.get(pk=int(post['fahrer_vormittag']))
			else:
				fahrtag.fahrer_vormittag=None
			if post['fahrer_nachmittag'] != "":
				fahrtag.fahrer_nachmittag=Fahrer.objects.get(pk=int(post['fahrer_nachmittag']))
			else:
				fahrtag.fahrer_nachmittag=None
			fahrtag.updated_by = request.user
			fahrtag.save()
			context['form'] = form
			messages.success(request, 'Fahrtag "<a href="'+request.path+'">'+post['datum']+' Bus '+post['team']+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Einsatztage/fahrer/')

		return render(request, self.template_name, context)		

class BueroView(MyListView):
	pass

class BueroDetailView(MyDetailView):
	pass

