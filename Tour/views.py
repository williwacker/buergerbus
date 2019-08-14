from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from jet.filters import RelatedFieldAjaxListFilter
from formtools.wizard.views import SessionWizardView

from .forms import TourAddForm1, TourAddForm2, TourChgForm
from .utils import DistanceMatrix

from .models import Tour
from Klienten.models import Klienten
from Einsatztage.models import Fahrtag

from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf
from datetime import datetime, timedelta, time

class MyListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL

class MyDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	initial = {'key': 'value'}

class TourenView(MyListView):
	template_name = 'Tour/touren.html'
	context_object_name = 'touren_liste'

	def get_queryset(self):
		return Tour.objects.order_by('bus','datum','uhrzeit').filter(bus__in=get_bus_list(self.request))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar()
		return context

class TourSave():
	def __init__(self, post):
		klient = Klienten.objects.get(pk=kwargs['pk'])
		fahrtag = Fahrtag.objects.get(pk=int(post['datum']))
		startzeit = datetime.strptime(post['uhrzeit'], '%H:%M:%S').time()
		googleList = DistanceMatrix().getMatrix(
			Klienten.objects.get(pk=int(post['abholklient'])), 
			Klienten.objects.get(pk=int(post['zielklient'])), 
			fahrtag.datum, 
			startzeit)
		tour = Tour(	
			klient=klient,
			datum=fahrtag,
			uhrzeit=post['uhrzeit'],            
			abholklient=Klienten.objects.get(pk=int(post['abholklient'])),
			zielklient=Klienten.objects.get(pk=int(post['zielklient'])),
			bus=klient.bus,
			entfernung=googleList[0],
			ankunft=googleList[2],
			updated_by=request.user
		)
		tour.save()

# Dies ist ein zweistufiger Prozess, der zuerst den Klient auswählen lässt, um im zweiten Bildschirm dann mithilfe des dem Klienten zugeordneten Busses
# die richtigen Fahrtage auszuwählen für das Datumsfeld. An den zweiten Bildschirm wird über die URL die KlientenId übergeben.
class TourAddView(MyDetailView):
	login_url = settings.LOGIN_URL
	template_name = 'Tour/tour_add.html'
	form_class = TourAddForm1

	def get(self, request, *args, **kwargs):
		form = self.form_class(initial=self.initial)
		# nur managed klienten anzeigen
		form.fields['fahrgast'].queryset = Klienten.objects.order_by('name').filter(typ='F', bus__in=get_bus_list(request))
		sidebar_liste = get_sidebar()
		return render(request, self.template_name, {'form': form, 
													'sidebar_liste': sidebar_liste})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		sidebar_liste = get_sidebar()
		if form.is_valid():
			post = request.POST.dict()
			return HttpResponseRedirect('/Tour/tour/add/'+post['fahrgast'])

		return render(request, self.template_name, {'form': form, 'sidebar_liste': sidebar_liste})

class TourAddView2(MyDetailView):
	form_class = TourAddForm2
	initial = {'key': 'value'}
	template_name = 'Tour/tour_add.html'
	
	def get(self, request, *args, **kwargs):
		form = self.form_class(initial=self.initial)
		sidebar_liste = get_sidebar()
		klient = Klienten.objects.get(pk=kwargs['pk'])
		self.initial['klient'] = klient.name
		self.initial['bus'] = klient.bus
		form.fields['datum'].queryset = Fahrtag.objects.order_by('datum').filter(archiv=False, team_id=klient.bus)
		form.fields['abholklient'].queryset = Klienten.objects.order_by('name').filter(bus__in=get_bus_list(request))
		form.fields['zielklient'].queryset = Klienten.objects.order_by('name').filter(bus__in=get_bus_list(request))
		return render(request, self.template_name, {'form': form, 
													'sidebar_liste': sidebar_liste})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		sidebar_liste = get_sidebar()
		if form.is_valid():
			TourSave(request.POST.dict())			
			return HttpResponseRedirect('/Tour/touren/')

		return render(request, self.template_name, {'form': form, 'sidebar_liste': sidebar_liste})

class TourChangeView(MyDetailView):
	login_url = settings.LOGIN_URL
	form_class = TourChgForm
	initial = {'key': 'value'}
	template_name = 'Tour/tour_add.html'
	
	def get(self, request, *args, **kwargs):
		form = self.form_class(instance=Tour.objects.get(pk=kwargs['pk']))
		sidebar_liste = get_sidebar()
		return render(request, self.template_name, {'form': form, 
													'sidebar_liste': sidebar_liste})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		sidebar_liste = get_sidebar()
		if form.is_valid():
			TourSave(request.POST.dict())	
			return HttpResponseRedirect('/Tour/touren/')

		return render(request, self.template_name, {'form': form, 'sidebar_liste': sidebar_liste})		

class TourDeleteView(View):

	def get(self, request, *args, **kwargs):
		k = Tour.objects.get(pk=kwargs['pk'])
		k.delete()

		return HttpResponseRedirect('/Tour/touren/')