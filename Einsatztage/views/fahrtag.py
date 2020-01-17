from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.http import (FileResponse, Http404, HttpResponse,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from trml2pdf import trml2pdf

from Basis.utils import get_sidebar, url_args
from Basis.views import MyDetailView, MyListView, MyUpdateView, MyView
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Klienten.models import Klienten
from Team.models import Fahrer
from Tour.models import Tour

from ..filters import FahrtagFilter
from ..forms import FahrtagChgForm
from ..models import Fahrtag
from ..tables import FahrerTable, FahrtagTable, TourTable
from ..utils import FahrtageSchreiben


class FahrtageListView(MyListView):
	permission_required = 'Einsatztage.view_fahrtag'

	def get_queryset(self):
		if self.request.user.has_perm('Einsatztage.change_fahrtag'): FahrtageSchreiben()
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = Fahrtag.objects.order_by('datum','team').filter(archiv=False, team__in=get_bus_list(self.request))
		if team: qs = qs.filter(team=team)
		if sort: qs = qs.order_by(sort)
		table = FahrtagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrtage"
		context['filter'] = FahrtagFilter(self.request.GET, queryset=Fahrtag.objects.filter(archiv=False, team__in=get_bus_list(self.request)))
		context['url_args'] = url_args(self.request)
		return context

class FahrtageChangeView(MyUpdateView):
	form_class = FahrtagChgForm
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	model = Fahrtag
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrereinsatz ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		fahrer = Fahrer.objects.filter(benutzer=self.request.user, aktiv=True, team=instance.team).first()
		if not fahrer and instance.fahrer_vormittag != None:
			messages.error(self.request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' kann nicht von '+str(instance.fahrer_vormittag)+' gebucht werden.')
			return HttpResponseRedirect(self.success_url+url_args(self.request))	
		if not fahrer and instance.fahrer_nachmittag != None:
			messages.error(self.request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' kann nicht von '+str(instance.fahrer_nachmittag)+' gebucht werden.')
			return HttpResponseRedirect(self.success_url+url_args(self.request))	
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
		return super(FahrtageChangeView, self).form_valid(form)	

class FahrtageBookvView(MyView):
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	model = Fahrtag	

	def get(self, request, pk):
		instance = get_object_or_404(Fahrtag, pk=pk)
		fahrer = Fahrer.objects.filter(benutzer=request.user, aktiv=True, team=instance.team).first()
		if not fahrer:
			messages.error(request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' kann nicht von Ihnen gebucht werden.')
		elif instance.fahrer_vormittag != None:
			messages.error(request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' ist bereits gebucht.')
		else:
			instance.fahrer_vormittag = fahrer
			instance.save()
			messages.success(request, self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.')
		return HttpResponseRedirect(self.success_url+url_args(request))

class FahrtageBooknView(MyView):
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	model = Fahrtag	

	def get(self, request, pk):
		instance = get_object_or_404(Fahrtag, pk=pk)
		fahrer = Fahrer.objects.filter(benutzer=request.user, aktiv=True, team=instance.team).first()
		if not fahrer:
			messages.error(request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' kann nicht von Ihnen gebucht werden.')
		elif instance.fahrer_nachmittag != None:
			messages.error(request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' ist bereits gebucht.')
		else:
			instance.fahrer_nachmittag = fahrer
			instance.save()
			messages.success(request, self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.')
		return HttpResponseRedirect(self.success_url+url_args(request))

class FahrtageCancelvView(MyUpdateView):
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	model = Fahrtag	

	def get(self, request, pk):
		instance = get_object_or_404(Fahrtag, pk=pk)
		fahrer = Fahrer.objects.filter(benutzer=request.user, team=instance.team).first()
		if instance.fahrer_vormittag != fahrer:
			messages.error(request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' ist nicht auf Sie gebucht.')
		else:
			instance.fahrer_vormittag = None
			instance.save()
			messages.success(request, self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.')
		return HttpResponseRedirect(self.success_url+url_args(request))	

class FahrtageCancelnView(MyUpdateView):
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	model = Fahrtag	

	def get(self, request, pk):
		instance = get_object_or_404(Fahrtag, pk=pk)
		fahrer = Fahrer.objects.filter(benutzer=request.user, team=instance.team).first()
		if instance.fahrer_nachmittag != fahrer:
			messages.error(request, self.model._meta.verbose_name.title()+' am '+str(instance.datum)+' '+str(instance.team)+' ist nicht auf Sie gebucht.')
		else:
			instance.fahrer_nachmittag = None
			instance.save()
			messages.success(request, self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.')
		return HttpResponseRedirect(self.success_url+url_args(request))						