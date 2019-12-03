import subprocess
from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from django import forms
from Klienten.forms import StrassenAddForm, StrassenChgForm
from Klienten.models import Strassen, Orte
from Klienten.tables import StrassenTable
from Klienten.filters import StrassenFilter
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf, url_args
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView, MyDeleteView, MyCreateView

register = template.Library()

class StrassenView(MyListView):
	permission_required = 'Klienten.view_strassen'
	
	def get_queryset(self):
		ort = self.request.GET.get('ort')
		strasse = self.request.GET.get('strasse')
		qs = Strassen.objects.order_by('ort','strasse')
		if ort:
			qs = qs.filter(ort=ort)
		if strasse:
			qs = qs.filter(strasse=strasse)
		table = StrassenTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Strassen"
		if self.request.user.has_perm('Klienten.add_strassen'):
			context['add'] = "Strasse"
		context['filter'] = StrassenFilter(self.request.GET, queryset=Strassen.objects.all())
		context['url_args'] = url_args(self.request)
		return context

class StrassenAddView(MyCreateView):
	form_class = StrassenAddForm
	permission_required = 'Klienten.add_strassen'
	success_url = '/Klienten/strassen/'
	model = Strassen

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Strasse hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['popup'] = self.request.GET.get('_popup',None)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		ort = request.GET.get('ort')
		self.initial['ort'] = Orte.objects.get(id=str(ort)) if ort else None
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save()
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+str(instance)+' in '+str(instance.ort)+'</a>" wurde erfolgreich hinzugefügt.'
		self.success_url += url_args(self.request)
		return super(StrassenAddView, self).form_valid(form)	

class StrassenChangeView(MyUpdateView):
	form_class = StrassenChgForm
	permission_required = 'Klienten.change_strassen'
	success_url = '/Klienten/strassen/'
	model = Strassen

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Strasse ändern"
		if self.request.user.has_perm('Klienten.delete_strassen'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Strassen.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_message = 'Strasse "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+instance.strasse+'</a>" wurde erfolgreich geändert.'
		self.success_url += url_args(self.request)
		return super(StrassenChangeView, self).form_valid(form)			

class StrassenDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_strassen'
	success_url = '/Klienten/strassen/'
	model = Strassen
	pass