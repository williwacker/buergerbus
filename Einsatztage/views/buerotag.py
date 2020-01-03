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
from Einsatzmittel.utils import get_buero_list
from Team.models import Fahrer, Koordinator

from ..filters import BuerotagFilter
from ..forms import BuerotagChgForm
from ..models import Buerotag
from ..tables import BuerotagTable
from ..utils import BuerotageSchreiben


class BuerotageListView(MyListView):
	permission_required = 'Einsatztage.view_buerotag'
	
	def get_queryset(self):
		if self.request.user.has_perm('Einsatztage.change_buerotag'): BuerotageSchreiben()
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = Buerotag.objects.order_by('team','datum').filter(archiv=False, team__in=get_buero_list(self.request))
		if team: qs = qs.filter(team=team)
		if sort: qs = qs.order_by(sort)
		table = BuerotagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bürotage"
		context['filter'] = BuerotagFilter(self.request.GET, queryset=Buerotag.objects.filter(archiv=False, team__in=get_buero_list(self.request)))
		context['url_args'] = url_args(self.request)
		return context

class BuerotageChangeView(MyUpdateView):
	form_class = BuerotagChgForm
	permission_required = 'Einsatztage.change_buerotag'
	success_url = '/Einsatztage/buero/'
	model = Buerotag

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bürotag ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
		return super(BuerotageChangeView, self).form_valid(form)	