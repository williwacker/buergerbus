from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages

from .models import Fahrer, Buerokraft
from Einsatzmittel.models import Bus, Buero
from .forms import FahrerAddForm, FahrerChgForm, BuerokraftAddForm, BuerokraftChgForm
from .tables import FahrerTable, BuerokraftTable
from .filters import FahrerFilter, BuerokraftFilter
from Basis.utils import get_sidebar
from Einsatzmittel.utils import get_bus_list
from Basis.views import MyListView, MyDetailView, MyView

#from .views import BuerokraftView, BuerokraftAddView, BuerokraftChangeView, BuerokraftDeleteView

register = template.Library()

class FahrerView(MyListView):
	auth_name = 'Team.view_fahrer'

	def get_fg_queryset(self):
		return Fahrer.objects.order_by('team','name').filter(team__in=get_bus_list(self.request))

	def get_queryset(self):
		team = self.request.GET.get('team')
		qs = self.get_fg_queryset()
		if team:
			qs = qs.filter(team=team)
		return FahrerTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrer"
		context['add'] = "Fahrer"
		context['filter'] = FahrerFilter(self.request.GET, queryset=self.get_fg_queryset())
		return context

class FahrerAddView(MyDetailView):
	form_class = FahrerAddForm
	auth_name = 'Team.change_fahrer'

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
			messages.success(request, 'Fahrer "<a href="/Team/fahrer/'+str(fahrer.id)+'/">'+fahrer.name+' '+str(fahrer.team)+'</a>" wurde erfolgreich hinzugefügt.')
			return HttpResponseRedirect('/Team/fahrer/')
		return render(request, self.template_name, context)

class FahrerChangeView(MyDetailView):
	form_class = FahrerChgForm
	auth_name = 'Team.change_fahrer'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrer ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Fahrer.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		if form.is_valid():
			post = request.POST.dict()
			t = Bus.objects.get(pk=int(post['team']))
			fahrer = Fahrer.objects.get(pk=kwargs['pk'])
			fahrer.name=post['name']
			fahrer.email=post['email']
			fahrer.telefon=post['telefon']
			fahrer.mobil=post['mobil']
			fahrer.team=t
			if 'aktiv' in post:
				fahrer.aktiv = True
			else:
				fahrer.aktiv = False
			fahrer.updated_by = request.user
			fahrer.save()
			messages.success(request, 'Fahrer "<a href="'+request.path+'">'+fahrer.name+' '+str(fahrer.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Team/fahrer/')

		return render(request, self.template_name, context)		

class FahrerDeleteView(MyView):
	auth_name = 'Team.delete_fahrer'

	def get(self, request, *args, **kwargs):
		k = Fahrer.objects.get(pk=kwargs['pk'])
		k.delete()
		messages.success(request, 'Fahrer '+k.name+' wurde gelöscht.')
		return HttpResponseRedirect('/Team/fahrer/')