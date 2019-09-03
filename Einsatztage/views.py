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

from .tables import FahrtagTable, BuerotagTable
from .filters import FahrtagFilter, BuerotagFilter
from .utils import FahrtageSchreiben
from .forms import FahrtagChgForm, BuerotagChgForm
from .models import Fahrtag, Buerotag
from Tour.models import Tour
from Team.models import Fahrer, Buerokraft
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list, get_buero_list
from Basis.utils import get_sidebar

class MyListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/simple_table.html'
	context_object_name = 'table'

class MyDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'

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

class FahrtageListView(MyListView):
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

class FahrtageChangeView(MyDetailView):
	form_class = FahrtagChgForm
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrereinsatz ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
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
			messages.success(request, 'Fahrtag "<a href="'+request.path+'">'+str(fahrtag.datum)+' '+str(fahrtag.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Einsatztage/fahrer/')

		return render(request, self.template_name, context)		

class BuerotageListView(MyListView):
	
	def get_queryset(self):
		team = self.request.GET.get('team')
		qs = Buerotag.objects.order_by('team','datum')
		if team:
			qs = qs.filter(team=team)
		table = BuerotagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bürotage"
		context['filter'] = BuerotagFilter(self.request.GET, queryset=Buerotag.objects.all())
		return context

class BuerotageChangeView(MyDetailView):
	form_class = BuerotagChgForm

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Bürotag ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Buerotag.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		if form.is_valid():
			post = request.POST.dict()
			buero = Buerotag.objects.get(pk=kwargs['pk'])
			if post['mitarbeiter'] != "":
				buero.mitarbeiter=Buerokraft.objects.get(pk=int(post['mitarbeiter']))
			buero.updated_by = request.user
			buero.save()
			context['form'] = form
			messages.success(request, 'Bürotag "<a href="'+request.path+'">'+str(buero.datum)+' '+str(buero.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Einsatztage/buero/')
		else:
			messages.error(request, form.errors)

		return render(request, self.template_name, context)		