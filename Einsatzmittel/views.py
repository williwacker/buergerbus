from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_relation_dict, get_sidebar, url_args
from Basis.views import (MyDeleteView, MyCreateView, MyListView, MyUpdateView,
                         MyView)

from .forms import BueroChgForm, BusChgForm
from .models import Buero, Bus
from .tables import BueroTable, BusTable

register = template.Library()

class BusView(MyListView):
	permission_required = 'Einsatzmittel.view_bus'

	def get_queryset(self):
		return(BusTable(Bus.objects.order_by('bus')))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Busse"
		if self.request.user.has_perm('Einsatzmittel.add_bus'): context['add'] = "Bus"
		context['url_args'] = url_args(self.request)
		return context

class BusAddView(MyCreateView):
	form_class = BusChgForm
	permission_required = 'Einsatzmittel.add_bus'
	success_url = '/Einsatzmittel/busse/'
	model = Bus

	def get_context_data(self, **kwargs):
		context = super(BusAddView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bus hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_url += url_args(self.request)
		messages.success(self.request, 'Bus "<a href="'+self.success_url+str(instance.id)+'">'+instance.bus+'</a>" wurde erfolgreich hinzugefügt.')	
		return super(BusAddView, self).form_valid(form)


class BusChangeView(MyUpdateView):
	permission_required = 'Einsatzmittel.change_bus'
	form_class = BusChgForm
	model = Bus
	success_url = '/Einsatzmittel/busse/'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bus ändern"
		if self.request.user.has_perm('Einsatzmittel.delete_bus'): context['delete_button'] = "Löschen" 
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)		
		messages.success(self.request, self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance)+'</a>" wurde erfolgreich geändert.')
		return super(BusChangeView, self).form_valid(form) 


class BusDeleteView(MyDeleteView):
	permission_required = 'Einsatzmittel.delete_bus'
	model=Bus
	success_url = '/Einsatzmittel/busse/'
	pass

# Bueros 

class BueroView(MyListView):
	permission_required = 'Einsatzmittel.view_buero'

	def get_queryset(self):
		return(BueroTable(Buero.objects.order_by('buero')))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Büros"
		if self.request.user.has_perm('Einsatzmittel.add_buero'): context['add'] = "Büro"
		context['url_args'] = url_args(self.request)
		return context

class BueroAddView(MyCreateView):
	form_class = BueroChgForm
	permission_required = 'Einsatzmittel.add_buero'
	success_url = '/Einsatzmittel/bueros/'
	model = Buero

	def get_context_data(self, **kwargs):
		context = super(BueroAddView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Büro hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_url += url_args(self.request)
		messages.success(self.request, 'Büro "<a href="'+self.success_url+str(instance.id)+'">'+instance.buero+'</a>" wurde erfolgreich hinzugefügt.')		
		return super(BueroAddView, self).form_valid(form)


class BueroChangeView(MyUpdateView):
	permission_required = 'Einsatzmittel.change_buero'
	form_class = BueroChgForm
	model = Buero
	success_url = '/Einsatzmittel/bueros/'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Büro ändern"
		if self.request.user.has_perm('Einsatzmittel.delete_buero'): context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)
		messages.success(self.request, 'Büro "<a href="'+self.success_url+str(instance.id)+'">'+instance.buero+'</a>" wurde erfolgreich geändert.')
		return super(BueroChangeView, self).form_valid(form) 


class BueroDeleteView(MyDeleteView):
	permission_required = 'Einsatzmittel.delete_buero'
	success_url = '/Einsatzmittel/bueros/'
	model = Buero
	pass
