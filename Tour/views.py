from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from jet.filters import RelatedFieldAjaxListFilter
from django.contrib import messages

from .forms import TourAddForm1, TourAddForm2, TourChgForm
from .utils import DistanceMatrix, TourArchive, GuestCount
from .models import Tour
from .tables import TourTable
from .filters import TourFilter
from .navbars import tour_navbar
from Klienten.models import Klienten
from Einsatztage.models import Fahrtag

from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf, url_args, del_message
from datetime import datetime, timedelta, time
from Basis.views import MyListView, MyDetailView, MyView

class TourView(MyListView):
	permission_required = 'Tour.view_tour'
	
	def get_queryset(self):
		TourArchive()
		datum = self.request.GET.get('datum')
		qs = Tour.objects.order_by('bus','datum','uhrzeit').filter(archiv=False,bus__in=get_bus_list(self.request))
		if datum:
			qs = qs.filter(datum=datum)
		return TourTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Touren"
		if self.request.user.has_perm('Tour.add_tour'):
			context['add'] = "Tour"
		context['nav_bar'] = tour_navbar(Fahrtag.objects.order_by('datum').filter(archiv=False, team__in=get_bus_list(self.request),datum__gte=datetime.now(),datum__lte=datetime.now()+timedelta(settings.COUNT_TOUR_DAYS)),self.request.GET.get('datum'))
		context['url_args'] = url_args(self.request)
		return context	

# Dies ist ein zweistufiger Prozess, der zuerst den Klient auswählen lässt, um im zweiten Bildschirm dann mithilfe des dem Klienten zugeordneten Busses
# die richtigen Fahrtage auszuwählen für das Datumsfeld. An den zweiten Bildschirm wird über die URL die KlientenId übergeben.
class TourAddView(MyDetailView):
	form_class = TourAddForm1
	permission_required = 'Tour.add_tour'
	success_url = '/Tour/tour/'

	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour hinzufügen"
		context['submit_button'] = "Weiter"
		context['back_button'] = "Abbrechen"
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(initial=self.initial)
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
			storage = messages.get_messages(request)
			storage.used = True
			return HttpResponseRedirect(self.success_url+'add/'+post['fahrgast']+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)

class TourAddView2(MyDetailView):
	form_class = TourAddForm2
	permission_required = 'Tour.add_tour'
	success_url = '/Tour/tour/'
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Zurück"
		context['popup_button'] = {"id":"add_id_dienstleister","href":"/Klienten/dienstleister/add/","title":"Dienstleister hinzufügen","name":"Dienstleister"}
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(initial=self.initial)
		klient = Klienten.objects.get(pk=kwargs['pk'])
		self.initial['klient'] = klient.name
		self.initial['bus'] = klient.bus
		form.fields['datum'].queryset = Fahrtag.objects.order_by('datum').filter(archiv=False, team_id=klient.bus, datum__gt=datetime.now(), datum__lte=datetime.now()+timedelta(settings.COUNT_TOUR_DAYS))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			klient = Klienten.objects.get(name=post['klient'])
			fahrtag = Fahrtag.objects.get(pk=int(post['datum']))
			startzeit = datetime.strptime(post['uhrzeit'], '%H:%M').time()
			googleList = ()
			if settings.USE_GOOGLE:
				googleList = DistanceMatrix().getMatrix(
					Klienten.objects.get(pk=int(post['abholklient'])), 
					Klienten.objects.get(pk=int(post['zielklient'])), 
					fahrtag.datum, 
					startzeit)
			tour = Tour(	
				klient=klient,
				datum=fahrtag,
				uhrzeit=post['uhrzeit'],
				personenzahl=post['personenzahl'],      
				abholklient=Klienten.objects.get(pk=int(post['abholklient'])),
				zielklient=Klienten.objects.get(pk=int(post['zielklient'])),
				bemerkung=post['bemerkung'],
				bus=klient.bus,
				updated_by=request.user
			)
			if form.cleaned_data['zustieg']:
				tour.zustieg=form.cleaned_data['zustieg']
			if googleList:
				tour.entfernung=googleList[0]
				tour.ankunft=googleList[2]
			tour.save()
			storage = messages.get_messages(request)
			storage.used = True
			messages.success(request, 'Tour "<a href="'+self.success_url+str(tour.id)+'/">'+tour.klient.name+' am '+str(tour.datum)+' um '+str(tour.uhrzeit) +'</a>" wurde erfolgreich hinzugefügt.')
			if url_args(request):
				return HttpResponseRedirect(self.success_url+url_args(request)+'&datum='+post['datum'])
			return HttpResponseRedirect(self.success_url+'?datum='+post['datum'])
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)

class TourChangeView(MyDetailView):
	form_class = TourChgForm
	permission_required = 'Tour.change_tour'
	success_url = '/Tour/tour/'
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Tour ändern"
		if self.request.user.has_perm('Tour.delete_tour'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		klient = Klienten.objects.get(pk=kwargs['pk'])
		instance=Tour.objects.get(pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields["fahrgast"].initial = instance.klient.name
		form.fields["bus_2"].initial = instance.bus
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			fahrtag = Fahrtag.objects.get(pk=int(post['datum']))
			startzeit = datetime.strptime(post['uhrzeit'][:5], '%H:%M').time()
			googleList = ()
			if settings.USE_GOOGLE:
				googleList = DistanceMatrix().getMatrix(
					Klienten.objects.get(pk=int(post['abholklient'])), 
					Klienten.objects.get(pk=int(post['zielklient'])), 
					fahrtag.datum, 
					startzeit)
			tour = Tour.objects.get(pk=kwargs['pk'])
			tour.datum=fahrtag
			tour.uhrzeit=post['uhrzeit']
			tour.zustieg=form.cleaned_data['zustieg']
			tour.personenzahl=post['personenzahl']
			tour.bemerkung=post['bemerkung']
			tour.abholklient=Klienten.objects.get(pk=int(post['abholklient']))
			tour.zielklient=Klienten.objects.get(pk=int(post['zielklient']))
			if googleList:
				tour.entfernung=googleList[0]
				tour.ankunft=googleList[2]
			tour.updated_by=request.user
			tour.save()
			storage = messages.get_messages(request)
			storage.used = True
			messages.success(request, 'Tour "<a href="'+request.path+url_args(request)+'">'+tour.klient.name+' am '+str(tour.datum)+' um '+str(tour.uhrzeit) +'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)		

class TourDeleteView(MyView):
	permission_required = 'Tour.delete_tour'
	success_url = '/Tour/tour/'

	def get(self, request, *args, **kwargs):
		k = Tour.objects.get(pk=kwargs['pk'])
		k.delete()
		messages.success(request, 'Tour '+k.klient.name+' am '+str(k.datum)+' um '+str(k.uhrzeit)+' wurde gelöscht.')
		return HttpResponseRedirect(self.success_url+url_args(request))
