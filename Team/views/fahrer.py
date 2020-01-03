from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyDeleteView, MyCreateView, MyListView, MyUpdateView,
                         MyView)
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list

from ..filters import FahrerFilter
from ..forms import FahrerAddForm, FahrerChgForm
from ..models import Fahrer
from ..tables import FahrerTable

register = template.Library()

class FahrerView(MyListView):
	permission_required = 'Team.view_fahrer'

	def get_fg_queryset(self):
		return Fahrer.objects.order_by('team','benutzer').filter(team__in=get_bus_list(self.request))

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

class FahrerAddView(MyCreateView):
	form_class = FahrerAddForm
	permission_required = 'Team.add_fahrer'
	success_url = '/Team/fahrer/'
	model = Fahrer

	def get_context_data(self, **kwargs):
		context = super(FahrerAddView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrer hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+str(", ".join([instance.benutzer.last_name,instance.benutzer.first_name]))+' '+str(instance.team)+'</a>" wurde erfolgreich hinzugefügt.'
		self.success_url += url_args(self.request)
		return super(FahrerAddView, self).form_valid(form)	

class FahrerChangeView(MyUpdateView):
	form_class = FahrerChgForm
	permission_required = 'Team.change_fahrer'
	success_url = '/Team/fahrer/'
	model = Fahrer

	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrer ändern"
		if self.request.user.has_perm('Team.delete_fahrer'): context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		instance = get_object_or_404(Fahrer, pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields['name'].initial = ", ".join([instance.benutzer.last_name, instance.benutzer.first_name])
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(", ".join([instance.benutzer.last_name,instance.benutzer.first_name]))+'</a>" wurde erfolgreich geändert.'
		return super(FahrerChangeView, self).form_valid(form) 

class FahrerDeleteView(MyDeleteView):
	permission_required = 'Team.delete_fahrer'
	success_url = '/Team/fahrer/'
	model = Fahrer
	pass