import logging
from datetime import datetime, time, timedelta

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from jet.filters import RelatedFieldAjaxListFilter

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)
from Einsatzmittel.utils import get_bus_list
from Einsatztage.models import Fahrtag
from Klienten.models import Klienten

from .filters import TourFilter
from .forms import TourAddForm1, TourAddForm2, TourChgForm
from .models import Tour
from .navbars import tour_navbar
from .tables import TourTable
from .utils import DistanceMatrix, GuestCount, TourArchive

logger = logging.getLogger(__name__)

class TourView(MyListView):
	permission_required = 'Tour.view_tour'
	
	def get_queryset(self):
		TourArchive()
		datum = self.request.GET.get('datum')
		qs = Tour.objects.order_by('bus','datum','uhrzeit').filter(archiv=False,bus__in=get_bus_list(self.request))
		if datum: qs = qs.filter(datum=datum)
		return TourTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Touren"
		if self.request.user.has_perm('Tour.add_tour'): context['add'] = "Tour"
		context['nav_bar'] = tour_navbar(Fahrtag.objects.order_by('datum').filter(archiv=False, urlaub=False, team__in=get_bus_list(self.request),datum__gte=datetime.now(),datum__lte=datetime.now()+timedelta(settings.COUNT_TOUR_DAYS)),self.request.GET.get('datum'))
		context['url_args'] = url_args(self.request)
		return context	

# Dies ist ein zweistufiger Prozess, der zuerst den Klient auswählen lässt, um im zweiten Bildschirm dann mithilfe des dem Klienten zugeordneten Busses
# die richtigen Fahrtage auszuwählen für das Datumsfeld. An den zweiten Bildschirm wird über die URL die KlientenId übergeben.
class TourAddView(MyCreateView):
	form_class = TourAddForm1
	permission_required = 'Tour.add_tour'
	success_url = '/Tour/tour/'
	model = Tour

	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour hinzufügen"
		context['submit_button'] = "Weiter"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		form = self.form_class()
		# nur managed klienten anzeigen
		form.fields['fahrgast'].queryset = Klienten.objects.order_by('name').filter(typ='F', bus__in=get_bus_list(request))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			return HttpResponseRedirect(self.success_url+'add/'+post['fahrgast']+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)

class TourAddView2(MyCreateView):
	form_class = TourAddForm2
	permission_required = 'Tour.add_tour'
	success_url = '/Tour/tour/'
	model = Tour
	
	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Zurück","javascript:history.go(-1)"]
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		klient = get_object_or_404(Klienten, pk=kwargs['pk'])
		self.initial['klient'] = klient
		self.initial['fahrgast'] = klient
		self.initial['bus'] = klient.bus
		self.initial['bus_2'] = klient.bus
		self.initial['abholklient'] = klient
		self.initial['zielklient'] = klient
		fahrtag = request.GET.get('datum')
		self.initial['datum'] = Fahrtag.objects.filter(id=fahrtag, team_id=klient.bus_id).first() if fahrtag else None
		form = self.form_class(initial=self.initial)
		form.fields['datum'].queryset = Fahrtag.objects.order_by('datum').filter(archiv=False, urlaub=False, team_id=klient.bus_id, datum__gt=datetime.now(), datum__lte=datetime.now()+timedelta(klient.bus.plantage))
		qs = Tour.objects.filter(klient__id=klient.id).values_list('abholklient',flat=True).distinct()
		form.fields['abholfavorit'].queryset = Klienten.objects.filter(id__in=qs).order_by('name')	| Klienten.objects.filter(id=klient.id)
		form.fields['abholklient'].queryset  = Klienten.objects.filter(typ='D').order_by('name')   	| Klienten.objects.filter(id=klient.id)
		qs = Tour.objects.filter(klient__id=klient.id).values_list('zielklient',flat=True).distinct()
		form.fields['zielfavorit'].queryset  = Klienten.objects.filter(id__in=qs).order_by('name') 	| Klienten.objects.filter(id=klient.id)
		form.fields['zielklient'].queryset   = Klienten.objects.filter(typ='D').order_by('name')   	| Klienten.objects.filter(id=klient.id)
		if 'instance' in locals() and instance.konflikt:
			messages.error(request, instance.konflikt)
		else:
			form.fields['konflikt_ignorieren'].widget = forms.HiddenInput()
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_url += '?datum='+str(instance.datum_id)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+instance.klient.name+' am '+str(instance.datum)+' um '+str(instance.uhrzeit) +'</a>" wurde erfolgreich hinzugefügt.'
		logger.info("Koordinator={} Fahrgast={} Start={} {} Abholklient={} Zielklient={}".format(self.request.user, instance.klient.name, str(instance.datum), str(instance.uhrzeit), instance.abholklient, instance.zielklient))
		if instance.konflikt != '':
			messages.error(self.request, instance.konflikt)
		return super(TourAddView2, self).form_valid(form)

class TourChangeView(MyUpdateView):
	form_class = TourChgForm
	permission_required = 'Tour.change_tour'
	success_url = '/Tour/tour/'
	model = Tour
	
	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour ändern"
		if self.request.user.has_perm('Tour.delete_tour'): context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		instance=get_object_or_404(Tour, pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields["fahrgast"].initial = instance.klient.name
		form.fields["id"].initial = instance.id
		form.fields['datum'].queryset = Fahrtag.objects.order_by('datum').filter(archiv=False, urlaub=False, team=instance.fahrgast.bus, datum__gt=datetime.now(), datum__lte=datetime.now()+timedelta(instance.bus.plantage))
		qs = Tour.objects.filter(klient__id=instance.klient.id).values_list('abholklient',flat=True).distinct()
		form.fields['abholfavorit'].queryset = Klienten.objects.filter(id__in=qs).order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		form.fields['abholklient'].queryset  = Klienten.objects.filter(typ='D').order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		qs = Tour.objects.filter(klient__id=instance.klient.id).values_list('zielklient',flat=True).distinct()
		form.fields['zielfavorit'].queryset  = Klienten.objects.filter(id__in=qs).order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		form.fields['zielklient'].queryset   = Klienten.objects.filter(typ='D').order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		form.fields['bus_2'].initial = instance.bus
		if instance.konflikt:
			messages.error(request, instance.konflikt)
		else:
			form.fields['konflikt_ignorieren'].widget = forms.HiddenInput()
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += '?datum='+str(instance.datum_id)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+instance.klient.name+' am '+str(instance.datum)+' um '+str(instance.uhrzeit) +'</a>" wurde erfolgreich geändert.'
		logger.info("Koordinator={} Fahrgast={} Start={} {} Abholklient={} Zielklient={}".format(self.request.user, instance.klient.name, str(instance.datum), str(instance.uhrzeit), instance.abholklient, instance.zielklient))
		if instance.konflikt != '':
			messages.error(self.request, instance.konflikt)
		return super(TourChangeView, self).form_valid(form)	

class TourCopyView(MyUpdateView):
	form_class = TourChgForm
	permission_required = 'Tour.change_tour'
	success_url = '/Tour/tour/'
	model = Tour
	
	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour ändern"
		if self.request.user.has_perm('Tour.delete_tour'): context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		instance=get_object_or_404(Tour, pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields["fahrgast"].initial = instance.klient.name
		form.fields["id"].initial = instance.id
		form.fields['datum'].queryset = Fahrtag.objects.order_by('datum').filter(archiv=False, urlaub=False, team=instance.fahrgast.bus, datum__gt=datetime.now(), datum__lte=datetime.now()+timedelta(instance.bus.plantage))
		qs = Tour.objects.filter(klient__id=instance.klient.id).values_list('abholklient',flat=True).distinct()
		form.fields['abholfavorit'].queryset = Klienten.objects.filter(id__in=qs).order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		form.fields['abholklient'].queryset  = Klienten.objects.filter(typ='D').order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		qs = Tour.objects.filter(klient__id=instance.klient.id).values_list('zielklient',flat=True).distinct()
		form.fields['zielfavorit'].queryset  = Klienten.objects.filter(id__in=qs).order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		form.fields['zielklient'].queryset   = Klienten.objects.filter(typ='D').order_by('name') 	| Klienten.objects.filter(id=instance.klient.id)
		form.fields['bus_2'].initial = instance.bus
		if instance.konflikt:
			messages.error(request, instance.konflikt)
		else:
			form.fields['konflikt_ignorieren'].widget = forms.HiddenInput()
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.pk = None
		instance.save()
		self.success_url += '?datum='+str(instance.datum_id)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+instance.klient.name+' am '+str(instance.datum)+' um '+str(instance.uhrzeit) +'</a>" wurde erfolgreich hinzugefügt.'
		logger.info("Koordinator={} Fahrgast={} Start={} {} Abholklient={} Zielklient={}".format(self.request.user, instance.klient.name, str(instance.datum), str(instance.uhrzeit), instance.abholklient, instance.zielklient))
		if instance.konflikt != '':
			messages.error(self.request, instance.konflikt)
		return super(TourCopyView, self).form_valid(form)			

class TourDeleteView(MyDeleteView):
	permission_required = 'Tour.delete_tour'
	success_url = '/Tour/tour/'
	model = Tour
	pass
