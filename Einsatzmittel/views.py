from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Bus, Buero
from .forms import BusChgForm, BueroChgForm
from .tables import BusTable, BueroTable
from Basis.utils import get_sidebar
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView

register = template.Library()

class BusView(MyListView):
	auth_name = 'Einsatzmittel.view_bus'

	def get_queryset(self):
		return(BusTable(Bus.objects.order_by('bus')))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Busse"
		context['add'] = "Bus"
		return context

class BusAddView(MyDetailView):
	form_class = BusChgForm
	auth_name = 'Einsatzmittel.change_bus'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Bus hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/Einsatzmittel/busse/')
		return render(request, self.template_name, context)

class BusChangeView(MyUpdateView):
	auth_name = 'Einsatzmittel.change_bus'
	form_class = BusChgForm
	model=Bus
	success_url = '/Einsatzmittel/busse/'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bus ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context

class BusDeleteView(MyView):
	auth_name = 'Einsatzmittel.delete_bus'

	def get(self, request, *args, **kwargs):
		b = Bus.objects.get(pk=kwargs['pk'])
		bus = str(b)
		b.delete()
		messages.success(request, bus+' wurde gelöscht.')
		return HttpResponseRedirect('/Einsatzmittel/busse/')

# Bueros 

class BueroView(MyListView):
	auth_name = 'Einsatzmittel.view_buero'

	def get_queryset(self):
		return(BueroTable(Buero.objects.order_by('buero')))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Büros"
		context['add'] = "Büro"
		return context

class BueroAddView(MyDetailView):
	form_class = BueroChgForm
	auth_name = 'Einsatzmittel.change_buero'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Büro hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/Einsatzmittel/bueros/')
		return render(request, self.template_name, context)

class BueroChangeView(MyUpdateView):
	auth_name = 'Einsatzmittel.change_buero'
	form_class = BueroChgForm
	model=Buero
	success_url = '/Einsatzmittel/bueros/'
	success_message = 'Büro erfolgreich geändert'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Büro ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context

class BueroDeleteView(MyView):
	auth_name = 'Einsatzmittel.delete_buero'

	def get(self, request, *args, **kwargs):
		b = Buero.objects.get(pk=kwargs['pk'])
		buero = str(b)
		b.delete()
		messages.success(request, 'Büro '+buero+' wurde gelöscht.')
		return HttpResponseRedirect('/Einsatzmittel/bueros/')		