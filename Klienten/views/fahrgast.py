import subprocess
from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from django import forms
from Klienten.forms import FahrgastAddForm, FahrgastChgForm
from Klienten.models import Klienten, Orte, Strassen
from Klienten.tables import FahrgaesteTable
from Klienten.filters import FahrgaesteFilter
from Klienten.utils import GeoLocation
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Einsatztage.views import FahrplanAsPDF
from Basis.utils import get_sidebar, render_to_pdf, url_args
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView, MyDeleteView, MyCreateView

register = template.Library()

class FahrgastView(MyListView):
	permission_required = 'Klienten.view_klienten'

	def get_fg_queryset(self):
		allow = settings.ALLOW_OUTSIDE_CLIENTS
		if allow:
			return Klienten.objects.order_by('name','ort').filter(typ='F', bus__in=get_bus_list(self.request)) | Klienten.objects.order_by('name','ort').filter(typ='F', bus__isnull=True)
		else:
			return Klienten.objects.order_by('name','ort').filter(typ='F', bus__in=get_bus_list(self.request))

	def get_queryset(self):
		ort = self.request.GET.get('ort')
		bus = self.request.GET.get('bus')
		sort = self.request.GET.get('sort')
		qs = self.get_fg_queryset()
		if ort:
			qs = qs.filter(ort=ort)
		if bus:
			qs = qs.filter(bus=bus)
		if sort:
			qs = qs.order_by(sort)
		return FahrgaesteTable(qs)


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrgäste"
		if self.request.user.has_perm('Klienten.add_klienten'):
			context['add'] = "Fahrgast"
		context['url_args'] = url_args(self.request)
		context['filter'] = FahrgaesteFilter(self.request.GET, queryset=self.get_fg_queryset())
		return context

class FahrgastAddView(MyCreateView):
	form_class = FahrgastAddForm
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/fahrgaeste/'
	model = Klienten

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['popup'] = self.request.GET.get('_popup',None)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(initial=self.initial)
		# nur managed orte anzeigen
		allow = settings.ALLOW_OUTSIDE_CLIENTS
		if allow:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
		else:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		if instance.ort.bus != None:
			instance.bus=instance.ort.bus
		if instance.latitude == 0 or set(['ort','strasse','hausnr']).intersection(set(form.changed_data)):
			GeoLocation().getLocation(instance)
		instance.updated_by = self.request.user
		instance.save()
		self.success_message = 'Fahrgast "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+instance.name+'</a>" wurde erfolgreich hinzugefügt.'
		self.success_url += url_args(self.request)
		return super(FahrgastAddView, self).form_valid(form)	

class FahrgastChangeView(MyUpdateView):
	form_class = FahrgastChgForm
	permission_required = 'Klienten.change_klienten'
	success_url = '/Klienten/fahrgaeste/'
	model = Klienten

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast ändern"
		if request.user.has_perm('Klienten.delete_klienten'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Klienten.objects.get(pk=kwargs['pk']))
		# nur managed orte anzeigen
		allow = settings.ALLOW_OUTSIDE_CLIENTS
		if allow:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
		else:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
		if form.instance.ort.bus != None:
			form.fields['bus'].widget = forms.HiddenInput()
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		if instance.ort.bus != None:
			instance.bus=instance.ort.bus
		if instance.latitude == 0 or set(['ort','strasse','hausnr']).intersection(set(form.changed_data)):
			GeoLocation().getLocation(instance)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_message = 'Fahrgast "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+instance.name+'</a>" wurde erfolgreich geändert.'
		self.success_url += url_args(self.request)
		return super(FahrgastChangeView, self).form_valid(form)	

class FahrgastDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_klienten'
	success_url = '/Klienten/fahrgaeste/'
	model = Klienten
	pass

class DSGVOView(MyDetailView):
	permission_required = 'Klienten.view_klienten'
	success_url = '/Klienten/fahrgaeste/'
	template_name = 'Klienten/dsgvo.html'
	context_object_name = 'klient'

	def get_queryset(self):
		return Klienten.objects.filter(pk=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "DSGVO anzeigen"
		context['back_button'] = ["Zurück",self.success_url+url_args(self.request)]
		return context 

class DSGVOasPDFView(MyView):
	permission_required = 'Klienten.view_klienten'
	success_url = '/Klienten/fahrgaeste/'

	def get(self, request, id):
		klient = Klienten.objects.get(pk=id)
		context = {'klient':klient}
		filename = "DSGVO_{}_{}.pdf".format(klient.nachname, klient.vorname)
		pdf = FahrplanAsPDF().pdf_render_to_response('Klienten/dsgvo.rml', context, filename)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			content = "inline; filename='%s'" %(filename)
			filepath = settings.DSGVO_PATH + filename
			try:
				with open(filepath, 'wb') as f:
					f.write(response.content)
				f.close()
				subprocess.Popen([filepath],shell=True)
				response['Content-Disposition'] = 'attachment; filename=' + filename
				return response
			except:
				messages.error(request, 'Dokument <b>'+filename+'</b> ist noch geöffnet.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		return HttpResponse("Kein Dokument vorhanden")		