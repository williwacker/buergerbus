from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from .forms import KlientenAddForm, KlientenChgForm, StammdatenFormSet

from .models import Klienten, Orte, Strassen
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf

class MyListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL

class MyDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL

class FahrgastView(MyListView):
	template_name = 'Klienten/fahrgast.html'
	context_object_name = 'klienten_liste'

	def get_queryset(self):
		allow = settings.ALLOW_OUTSIDE_CLIENTS
		if allow:
			return Klienten.objects.order_by('name','ort').filter(typ='F', bus__in=get_bus_list(self.request)) | Klienten.objects.order_by('name','ort').filter(typ='F', bus__isnull=True)
		else:
			return Klienten.objects.order_by('name','ort').filter(typ='F', bus__in=get_bus_list(self.request))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar()
		return context

class FahrgastAddView(MyDetailView):
	form_class = KlientenAddForm
	initial = {'key': 'value'}
	template_name = 'Klienten/fahrgast_add.html'
	
	def get(self, request, *args, **kwargs):
		form = self.form_class(initial=self.initial)
		# nur managed orte anzeigen
		allow = settings.ALLOW_OUTSIDE_CLIENTS
		if allow:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
		else:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
		sidebar_liste = get_sidebar()
		return render(request, self.template_name, {'form': form, 
													'sidebar_liste': sidebar_liste})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		sidebar_liste = get_sidebar()
		if form.is_valid():
			post = request.POST.dict()
			o = Orte.objects.get(pk=int(post['ort']))
			s = Strassen.objects.get(pk=int(post['strasse']))
			klient = Klienten(	name=post['name'], 
								telefon=post['telefon'],
								mobil=post['mobil'],
								ort=o,
								strasse=s,
								hausnr=post['hausnr'],
								dsgvo='01',
								bemerkung=post['bemerkung'],
								typ='F',
								bus=o.bus
							)
			klient.save()
			messages.success(request, 'Form submission successful')
			return HttpResponseRedirect('/Klienten/fahrgaeste/')

		return render(request, self.template_name, {'form': form, 'sidebar_liste': sidebar_liste})

class FahrgastChangeView(MyDetailView):
	login_url = settings.LOGIN_URL
	form_class = KlientenChgForm
	initial = {'key': 'value'}
	template_name = 'Klienten/fahrgast_add.html'
	
	def get(self, request, *args, **kwargs):
		form = self.form_class(instance=Klienten.objects.get(pk=kwargs['pk']))
		# nur managed orte anzeigen
#		form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
		sidebar_liste = get_sidebar()
		return render(request, self.template_name, {'form': form, 
													'sidebar_liste': sidebar_liste})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		sidebar_liste = get_sidebar()
		if form.is_valid():
			post = request.POST.dict()
			o = Orte.objects.get(pk=int(post['ort']))
			s = Strassen.objects.get(pk=int(post['strasse']))
			klient = Klienten.objects.get(pk=kwargs['pk'])
			klient.name=post['name']
			klient.telefon=post['telefon']
			klient.mobil=post['mobil']
			klient.ort=o
			klient.strasse=s
			klient.hausnr=post['hausnr']
#			klient.dsgvo='01'
			klient.bemerkung=post['bemerkung']
#			klient.typ='F'
			if (o.bus == None) & (post['bus'] != ''):
				klient.bus=Bus.objects.get(pk=int(post['bus']))
			klient.save()
			messages.success(request, 'Form submission successful')
			title = "Fahrgäste"
			return HttpResponseRedirect('/Klienten/fahrgaeste/')

		return render(request, self.template_name, {'form': form, 'sidebar_liste': sidebar_liste, 'messages' : messages, 'title' : title})		

class FahrgastDeleteView(View):

	def get(self, request, *args, **kwargs):
		k = Klienten.objects.get(pk=kwargs['pk'])
		k.delete()

		return HttpResponseRedirect('/Klienten/fahrgaeste/')

class DienstleisterAddView(MyDetailView):
	template_name = "Klienten/dienstleister_add.html"
	context_object_name = "klient"

	

class DSGVOView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	template_name = 'Klienten/dsgvo.html'
	context_object_name = 'klient'

	def get_queryset(self):
		return Klienten.objects.filter(pk=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar()
		return context

class DSGVOasPDFView(LoginRequiredMixin, View):
	login_url = settings.LOGIN_URL
	def get(self, request, id):
		klient = Klienten.objects.get(pk=id)
		context = {'klient':klient}
		pdf = render_to_pdf('Klienten/dsgvo.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "DSGVO_{}_{}.pdf".format(klient.nachname, klient.vorname)
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Kein Dokument vorhanden")

class DienstleisterView(MyListView):
	template_name = 'Klienten/dienstleister.html'
	context_object_name = 'klienten_liste'

	def get_queryset(self):
		return Klienten.objects.order_by('name','ort').filter(typ='D')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar()
		return context		


