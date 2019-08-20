from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from .forms import FahrgastAddForm, FahrgastChgForm, DienstleisterAddForm, DienstleisterChgForm, OrtAddForm

from .models import Klienten, Orte, Strassen
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf

register = template.Library()

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
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrgäste"
		return context

class FahrgastAddView(MyDetailView):
	form_class = FahrgastAddForm
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
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

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
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
								bus=o.bus,
								updated_by = request.user
							)
			klient.save()
			context['form'] = form		
			messages.success(request, 'Fahrgast "<a href="'+request.path+'">'+klient.name+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect('/Klienten/fahrgaeste/')
		
		return render(request, self.template_name, context)

class FahrgastChangeView(MyDetailView):
	form_class = FahrgastChgForm
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Klienten.objects.get(pk=kwargs['pk']))
		context['form'] = form

		# nur managed orte anzeigen
		allow = settings.ALLOW_OUTSIDE_CLIENTS
		if allow:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
		else:
			form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
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
			klient.bemerkung=post['bemerkung']
			if (o.bus == None) & (post['bus'] != ''):
				klient.bus=Bus.objects.get(pk=int(post['bus']))
			klient.updated_by = request.user
			klient.save()
			context['form'] = form
			messages.success(request, 'Fahrgast "<a href="'+request.path+'">'+klient.name+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Klienten/fahrgaeste/')

		return render(request, self.template_name, context)		

class FahrgastDeleteView(View):

	def get(self, request, *args, **kwargs):
		k = Klienten.objects.get(pk=kwargs['pk'])
		k.delete()

		return HttpResponseRedirect('/Klienten/fahrgaeste/')

class DSGVOView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	template_name = 'Klienten/dsgvo.html'
	context_object_name = 'klient'

	def get_queryset(self):
		return Klienten.objects.filter(pk=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "DSGVO anzeigen"
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
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dienstleister"
		return context		

class DienstleisterAddView(MyDetailView):
	form_class = DienstleisterAddForm
	initial = {'key': 'value'}
	template_name = "Basis/detail.html"

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Dienstleister hinzufügen"
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
			o = Orte.objects.get(pk=int(post['ort']))
			s = Strassen.objects.get(pk=int(post['strasse']))
			klient = Klienten(	name=post['name'], 
								telefon=post['telefon'],
								mobil=post['mobil'],
								ort=o,
								strasse=s,
								hausnr=post['hausnr'],
								dsgvo='99',
								bemerkung=post['bemerkung'],
								typ='D',
								updated_by = request.user
							)
			klient.save()
			context['form'] = form		
			messages.success(request, 'Dienstleister "<a href="'+request.path+'">'+klient.name+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect('/Klienten/dienstleister/')
		
		return render(request, self.template_name, context)

class DienstleisterChangeView(MyDetailView):
	form_class = DienstleisterChgForm
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Klienten.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
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
			klient.bemerkung=post['bemerkung']
			klient.updated_by = request.user
			klient.save()
			context['form'] = form
			messages.success(request, 'Dienstleister "<a href="'+request.path+'">'+klient.name+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Klienten/dienstleister/')

		return render(request, self.template_name, context)		

class DienstleisterDeleteView(View):

	def get(self, request, *args, **kwargs):
		k = Klienten.objects.get(pk=kwargs['pk'])
		k.delete()

		return HttpResponseRedirect('/Klienten/dienstleister/')	

class OrtView(MyListView):
	template_name = 'Klienten/orte.html'
	context_object_name = 'orte_liste'
	model = Orte
	
	def get_queryset(self):
		return Orte.objects.order_by('bus','ort')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Orte"
		return context		

class OrtAddView(MyDetailView):
	form_class = OrtAddForm
	initial = {'key': 'value'}
	template_name = "Basis/detail.html"

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Ort hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"		
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
		if form.is_valid():
			post = request.POST.dict()
			o = Orte.objects.get(pk=int(post['ort']))
			s = Strassen.objects.get(pk=int(post['strasse']))
			ort = Orte(	ort=Orte.objects.get(pk=int(post['ort'])),
						bus=Bus.objects.get(pk=int(post['bus'])),
						updated_by = request.user
					)
			ort.save()
			context['form'] = form		
			messages.success(request, 'Ort "<a href="'+request.path+'">'+ort.ort+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect('/Klienten/orte/')
		
		return render(request, self.template_name, context)

class OrtChangeView(MyDetailView):
	pass

class OrtDeleteView(View):
	pass