from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Fahrer, Koordinator
from Einsatzmittel.models import Bus, Buero
from .forms import FahrerAddForm, FahrerChgForm, KoordinatorAddForm, KoordinatorChgForm
from .tables import FahrerTable, KoordinatorTable
from .filters import FahrerFilter, KoordinatorFilter
from Basis.utils import get_sidebar, url_args, del_message
from Einsatzmittel.utils import get_bus_list, get_buero_list
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView, MyDeleteView

register = template.Library()

class FahrerView(MyListView):
	permission_required = 'Team.view_fahrer'

	def get_fg_queryset(self):
		if self.request.user.has_perm('Einsatzmittel.change_bus'):
			qs = Fahrer.objects.order_by('team','name')
		else:
			qs = Fahrer.objects.order_by('team','name').filter(team__in=get_bus_list(self.request))
		return qs

	def get_queryset(self):
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = self.get_fg_queryset()
		if team:
			qs = qs.filter(team=team)
		if sort:
			qs = qs.order_by(sort)
		return FahrerTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrer"
		if self.request.user.has_perm('Team.add_fahrer'):
			context['add'] = "Fahrer"
		context['filter'] = FahrerFilter(self.request.GET, queryset=self.get_fg_queryset())
		context['url_args'] = url_args(self.request)
		return context

class FahrerAddView(MyDetailView):
	form_class = FahrerAddForm
	permission_required = 'Team.add_fahrer'
	success_url = '/Team/fahrer/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrer hinzufügen"
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
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			fahrer = Fahrer(	name=post['name'], 
								email=post['email'],
								telefon=post['telefon'],
								mobil=post['mobil'],
								aktiv=True,
								team=Bus.objects.get(pk=int(post['team'])),
								updated_by = request.user
							)
			fahrer.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Fahrer(in) "<a href="'+self.success_url+str(fahrer.id)+url_args(request)+'/">'+fahrer.name+' '+str(fahrer.team)+'</a>" wurde erfolgreich hinzugefügt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)			
		return render(request, self.template_name, context)

class FahrerChangeView(MyUpdateView):
	form_class = FahrerChgForm
	permission_required = 'Team.change_fahrer'
	success_url = '/Team/fahrer/'
	model = Fahrer

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrer ändern"
		if self.request.user.has_perm('Team.delete_fahrer'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Fahrer.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_message = 'Fahrer(in) "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
		return super(FahrerChangeView, self).form_valid(form) 

class FahrerDeleteView(MyDeleteView):
	permission_required = 'Team.delete_fahrer'
	success_url = '/Team/fahrer/'
	model = Fahrer
	pass

# Koordinatoren 

class KoordinatorView(MyListView):
	permission_required = 'Team.view_koordinator'

	def get_fg_queryset(self):
		if self.request.user.has_perm('Einsatzmittel.change_buero'):
			qs = Koordinator.objects.order_by('team','benutzer')
		else:
			qs = Koordinator.objects.order_by('team','benutzer').filter(team__in=get_buero_list(self.request))
		return qs

	def get_queryset(self):
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = self.get_fg_queryset()
		if team:
			qs = qs.filter(team=team)
		if sort:
			qs = qs.order_by(sort)
		return KoordinatorTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Koordinator"
		if self.request.user.has_perm('Team.add_koordinator'):
			context['add'] = "Koordinator"
		context['filter'] = KoordinatorFilter(self.request.GET, queryset=self.get_fg_queryset())
		context['url_args'] = url_args(self.request)
		return context

class KoordinatorAddView(MyDetailView):
	form_class = KoordinatorAddForm
	permission_required = 'Team.add_koordinator'
	success_url = '/Team/koordinator/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Koordinator hinzufügen"
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
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			u = User.objects.get(pk=int(post['benutzer']))
			koordinator = Koordinator(
								benutzer=u, 
#								email=post['email'],
								telefon=post['telefon'],
								mobil=post['mobil'],
								aktiv=True,
								team=Buero.objects.get(pk=int(post['team'])),
								updated_by = request.user
							)
			koordinator.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Koordinator(in) "<a href="'+self.success_url+str(koordinator.id)+'/'+url_args(request)+'">'+str(koordinator.benutzer)+' '+str(koordinator.team)+'</a>" wurde erfolgreich hinzugefügt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)

class KoordinatorChangeView(MyUpdateView):
	form_class = KoordinatorChgForm
	permission_required = 'Team.change_koordinator'
	success_url = '/Team/koordinator/'
	model = Koordinator

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Koordinator ändern"
		if self.request.user.has_perm('Team.delete_koordinator'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		instance = Koordinator.objects.get(pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields['name'].initial = ", ".join([instance.benutzer.last_name, instance.benutzer.first_name])
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_message = 'Koordinator(in) "<a href="'+self.success_url+str(instance.id)+'">'+str(", ".join([instance.benutzer.last_name,instance.benutzer.first_name]))+'</a>" wurde erfolgreich geändert.'
		return super(KoordinatorChangeView, self).form_valid(form)	

class KoordinatorDeleteView(MyDeleteView):
	permission_required = 'Team.delete_koordinator'
	success_url = '/Team/koordinator/'
	model = Koordinator
	pass