from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyDeleteView, MyCreateView, MyListView, MyUpdateView,
                         MyView)
from Einsatzmittel.models import Buero
from Einsatzmittel.utils import get_buero_list

from ..filters import KoordinatorFilter
from ..forms import KoordinatorAddForm, KoordinatorChgForm
from ..models import Koordinator
from ..tables import KoordinatorTable

register = template.Library()


class KoordinatorView(MyListView):
	permission_required = 'Team.view_koordinator'

	def get_fg_queryset(self):
		return Koordinator.objects.order_by('team','benutzer').filter(team__in=get_buero_list(self.request))

	def get_queryset(self):
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = self.get_fg_queryset()
		if team: qs = qs.filter(team=team)
		if sort: qs = qs.order_by(sort)
		return KoordinatorTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Koordinator"
		if self.request.user.has_perm('Team.add_koordinator'): context['add'] = "Koordinator"
		context['filter'] = KoordinatorFilter(self.request.GET, queryset=self.get_fg_queryset())
		context['url_args'] = url_args(self.request)
		return context

class KoordinatorAddView(MyCreateView):
	form_class = KoordinatorAddForm
	permission_required = 'Team.add_koordinator'
	success_url = '/Team/koordinator/'
	model = Koordinator

	def get_context_data(self, **kwargs):
		context = super(KoordinatorAddView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Koordinator hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context
	
	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+str(", ".join([instance.benutzer.last_name,instance.benutzer.first_name]))+' '+str(instance.team)+'</a>" wurde erfolgreich hinzugefügt.'
		self.success_url += url_args(self.request)
		return super(KoordinatorAddView, self).form_valid(form)	

class KoordinatorChangeView(MyUpdateView):
	form_class = KoordinatorChgForm
	permission_required = 'Team.change_koordinator'
	success_url = '/Team/koordinator/'
	model = Koordinator

	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Koordinator ändern"
		if self.request.user.has_perm('Team.delete_koordinator'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		instance = get_object_or_404(Koordinator, pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields['name'].initial = ", ".join([instance.benutzer.last_name, instance.benutzer.first_name])
		context['form'] = form
		return render(request, self.template_name, context)
	
	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(", ".join([instance.benutzer.last_name,instance.benutzer.first_name]))+'</a>" wurde erfolgreich geändert.'
		return super(KoordinatorChangeView, self).form_valid(form)	

class KoordinatorDeleteView(MyDeleteView):
	permission_required = 'Team.delete_koordinator'
	success_url = '/Team/koordinator/'
	model = Koordinator
	pass
