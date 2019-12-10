import subprocess
from fuzzywuzzy import fuzz, process
from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from django import forms
from Klienten.forms import OrtAddForm, OrtChgForm
from Klienten.models import Orte
from Klienten.tables import OrteTable
from Klienten.filters import OrteFilter
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf, url_args
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView, MyDeleteView, MyCreateView

register = template.Library()

class OrtView(MyListView):
	permission_required = 'Klienten.view_orte'
	
	def get_queryset(self):
		ort = self.request.GET.get('ort')
		plz = self.request.GET.get('plz')
		bus = self.request.GET.get('bus')
		# nur managed orte anzeigen
		qs = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(self.request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
		if ort:
			qs = qs.filter(ort=ort)
		if plz:
			qs = qs.filter(plz=plz)
		if bus:
			qs = qs.filter(bus=bus)
		return OrteTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Orte"
		if self.request.user.has_perm('Klienten.add_orte'):
			context['add'] = "Ort"
		context['filter'] = OrteFilter(self.request.GET, queryset=Orte.objects.all())
		context['url_args'] = url_args(self.request)
		return context		

class OrtAddView(MyCreateView):
	form_class = OrtAddForm
	permission_required = 'Klienten.add_orte'
	success_url = '/Klienten/orte/'
	model = Orte

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Ort hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['popup'] = self.request.GET.get('_popup',None) 
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save()
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+str(instance)+'</a>" wurde erfolgreich hinzugefügt.'
		self.success_url += url_args(self.request)
		return super(OrtAddView, self).form_valid(form)	

class OrtChangeView(MyUpdateView):
	form_class = OrtChgForm
	permission_required = 'Klienten.change_orte'
	success_url = '/Klienten/orte/'
	model = Orte

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Ort ändern"
		if self.request.user.has_perm('Klienten.delete_orte'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Orte.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_message = 'Ort "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+instance.ort+'</a>" wurde erfolgreich geändert.'
		self.success_url += url_args(self.request)
		return super(OrtChangeView, self).form_valid(form)	

class OrtDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_orte'
	success_url = '/Klienten/orte/'
	model = Orte
	pass