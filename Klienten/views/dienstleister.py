import subprocess

from django import forms, template
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from fuzzywuzzy import fuzz, process
from jet.filters import RelatedFieldAjaxListFilter

from Basis.telefonbuch_suche import Telefonbuch
from Basis.utils import get_sidebar, url_args
from Basis.views import (MyDeleteView, MyCreateView, MyListView,
                         MyMultiFormsView, MyUpdateView)
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Einsatztage.views import FahrplanAsPDF
from Klienten.filters import DienstleisterFilter
from Klienten.forms import (DienstleisterAddForm, DienstleisterChgForm,
                            KlientenSearchForm, KlientenSearchResultForm)
from Klienten.models import DIENSTLEISTER_AUSWAHL, Klienten, Orte, Strassen
from Klienten.tables import DienstleisterTable
from Klienten.utils import GeoLocation

register = template.Library()

class DienstleisterView(MyListView):
	permission_required = 'Klienten.view_klienten'

	def get_queryset(self):
		name = self.request.GET.get('name')
		ort = self.request.GET.get('ort')
		kategorie = self.request.GET.get('kategorie')
		sort = self.request.GET.get('sort')
		qs = Klienten.objects.order_by('name','ort').filter(typ='D')
		if ort: qs = qs.filter(ort=ort)
		if name: qs = qs.filter(name=name)
		if kategorie: qs = qs.filter(kategorie=kategorie)
		if sort: qs = qs.order_by(sort)
		return DienstleisterTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dienstleister"
		if self.request.user.has_perm('Klienten.add_klienten'): context['add'] = "Dienstleister"
		context['filter'] = DienstleisterFilter(self.request.GET, queryset=Klienten.objects.order_by('name','ort').filter(typ='D'))
		context['url_args'] = url_args(self.request)
		return context		

class DienstleisterAddView(MyCreateView):
	form_class = DienstleisterAddForm
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/dienstleister/'
	model = Klienten

	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dienstleister hinzufügen"
		context['submit_button'] = "Sichern"
		context['popup'] = self.request.GET.get('_popup',None)
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		self.initial['typ'] = 'D'
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			instance = form.save(commit=False)
			instance.created_by = self.request.user
			instance.save()	
			messages.success(request, 'Dienstleister "<a href="'+self.success_url+str(instance.id)+'/'+url_args(request)+'">'+instance.name+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			if self.request.GET.get('_popup') == '1':
				return HttpResponse('''<script type="text/javascript">opener.location.reload(false);window.close();</script>''')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)

class DienstleisterChangeView(MyUpdateView):
	form_class = DienstleisterChgForm
	permission_required = 'Klienten.change_klienten'
	success_url = '/Klienten/dienstleister/'
	model = Klienten

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrgast ändern"
		if self.request.user.has_perm('Klienten.delete_klienten'): context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context
	
	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		if instance.latitude == 0 or set(['ort','strasse','hausnr']).intersection(set(form.changed_data)):
			GeoLocation().getLocation(instance)
		instance.save(force_update=True)
		self.success_message = 'Dienstleister "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich geändert.'
		self.success_url += url_args(self.request)
		return super(DienstleisterChangeView, self).form_valid(form)		

class DienstleisterDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_klienten'
	success_url = '/Klienten/dienstleister/'
	model = Klienten
	pass

class DienstleisterSearchMultiformsView(MyMultiFormsView):
	form_classes = {'suchen':KlientenSearchForm, 'anlegen':KlientenSearchResultForm }
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/dienstleister/'
	this_url    = '/Klienten/dienstleister/add/'
	manual_url  = '/Klienten/dienstleister/add/manual/'

	def get_context_data(self, **kwargs):
		context = super(DienstleisterSearchMultiformsView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dienstleister suchen und hinzufügen"
		context['submit_button'] = "Suchen"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['popup'] = self.request.GET.get('_popup',None)
		return context

	def get_suchen_initial(self):
		suchname = self.request.session.get('suchname','')
		suchort  = self.request.session.get('suchort','')		
		popup = self.request.GET.get('_popup')
		return {'suchname':suchname, 'suchort':suchort, '_popup':popup}

	def get_anlegen_initial(self):
		suchname = self.request.session.get('suchname','')
		suchort  = self.request.session.get('suchort','')
		choice   = self.request.session.get('clientsearch_choice','')
		result_list = []
		if suchname:
			result_list =  Telefonbuch().dasoertliche(suchname,suchort,'D')
			result_list += Telefonbuch().dastelefonbuch(suchname,suchort,'D')
			if not result_list:
				messages.error(self.request, 'Keinen Namen anhand der Suchkriterien gefunden')
			else:
				messages.success(self.request, 'Die folgenden Namen wurden gefunden:')
		return {'result_list':result_list, 'choice':choice}
	
	def create_anlegen_form(self, initial, prefix, data=None, files=None):
		result_list  = initial['result_list']
		choice = initial['choice']
		choices = []
		sel_choice = (0,'Adresse manuell eingeben')
		if result_list:
			for i in range(len(result_list)):
				# na = Name, pc = PLZ, ci = City, st = Street, hn = house-no, ph = phone, mph = mobile phone
				choices.append((i+1,'{} {} {} {} {}'.format(result_list[i]['na'],result_list[i]['pc'],result_list[i]['ci'],result_list[i]['st'],result_list[i]['hn'])))
				if i+1 == initial['choice']: sel_choice = choices[i]
		choices.append((0,'Adresse manuell eingeben'))

		form = self.form_classes['anlegen'](self.request.POST or None, initial={'suchergebnis':sel_choice})
		form.fields['suchergebnis'].choices=choices
		if not self.request.session.pop('city_create',False):
			form.fields['city_create'].widget = forms.HiddenInput()
		if not self.request.session.pop('force_create',False):
			form.fields['force_create'].widget = forms.HiddenInput()
		self.request.session['clientsearch_results'] = result_list
		return form

	def suchen_form_valid(self, form):
		if self.request.session.get('suchname','') != form.cleaned_data.get('suchname','A') \
		or self.request.session.get('suchort','')  != form.cleaned_data.get('suchort','A'):
			self.request.session.pop('clientsearch_choice','')
		self.request.session['suchname'] = form.cleaned_data['suchname']
		self.request.session['suchort']  = form.cleaned_data['suchort']
		return HttpResponseRedirect(self.this_url+url_args(self.request))	

	def anlegen_form_valid(self, form):
		if form.cleaned_data['suchergebnis'] == '0':
			messages.success(self.request, 'Bitte den Dienstleister manuell eingeben')
			return HttpResponseRedirect(self.manual_url+url_args(self.request))
		choice  = int(form.cleaned_data['suchergebnis'])
		self.request.session['clientsearch_choice'] = choice
		result = self.request.session.pop('clientsearch_results',[])[choice-1]
		self.create_dienstleister(result, force_create=form.cleaned_data.get('force_create',False), city_create=form.cleaned_data.get('city_create',False))
		return HttpResponseRedirect(self.this_url+url_args(self.request))
	
	def create_ort(self,plz,ort):
		ort = Orte(
			ort=ort,
			plz=plz
		)
		ort.save()
		messages.success(self.request, 'Ort "<a href="/Klienten/orte/'+str(ort.id)+'/'+'">'+str(ort)+'</a>" wurde erfolgreich hinzugefügt.')
		return

	def create_strasse(self,strasse,ort):
		orte=Orte.objects.get(ort=ort)
		strasse = strasse.replace('Str.','Straße')
		strasse = strasse.replace('str.','straße')
		strasse = Strassen(
			strasse=strasse,
			ort=orte
		)
		strasse.save()
		messages.success(self.request, 'Strasse "<a href="/Klienten/strassen/'+str(strasse.id)+'/'+'">'+str(strasse)+'</a>" wurde erfolgreich hinzugefügt.')
		return

	def create_dienstleister(self, result, force_create=False, city_create=False):
		# suche über die PLZ wird gemacht, um alle Orte und Vororte zu finden, da die telefonbuchsuche keinen Vorort liefert
		cities_by_zip = list(Orte.objects.values('ort','id').filter(plz=result['pc']))
		if not cities_by_zip:
			if self.request.user.has_perm('Klienten.add_orte'):
				if city_create:
					self.create_ort(plz=result['pc'], ort=result['ci'])
					cities_by_zip = list(Orte.objects.values('ort','id').filter(plz=result['pc']))
				else:
					messages.info(self.request, "Der gefundene Ort existiert noch nicht. Wenn Sie ihn anlegen wollen, bitte 'Ort und Strasse anlegen' anhaken.")
					self.request.session['city_create'] = True
					return HttpResponseRedirect(self.success_url+url_args(self.request))
			else:
				messages.info(self.request, "Der gefundene Ort existiert noch nicht, aber Sie haben keine Berechtigung um Orte anzulegen!")
				return HttpResponseRedirect(self.success_url+url_args(self.request))
		best_match = process.extract(result['ci'], [sub['ort'] for sub in cities_by_zip], scorer=fuzz.token_set_ratio, limit=100)  # for debugging only
		filtered_city_names = [sub[0] for sub in process.extract(result['ci'], [sub['ort'] for sub in cities_by_zip], scorer=fuzz.token_set_ratio) if sub[1]>=85]
		matching_cities = list(Orte.objects.values('ort','id').filter(ort__in=filtered_city_names))

		streets_by_city = list(Strassen.objects.values('strasse','ort','id').filter(ort_id__in=[sub['id'] for sub in matching_cities]))
		filtered_street_names = []
		if streets_by_city:
			filtered_street_names = [sub[0] for sub in process.extract(result['st'], [sub['strasse'] for sub in streets_by_city], scorer=fuzz.token_set_ratio) if sub[1]>=85]
		if not filtered_street_names:
			if self.request.user.has_perm('Klienten.add_strassen'):
				if city_create:
					self.create_strasse(strasse=result['st'], ort=result['ci'])
					streets_by_city = list(Strassen.objects.values('strasse','ort','id').filter(ort_id__in=[sub['id'] for sub in matching_cities]))
					filtered_street_names = [sub[0] for sub in process.extract(result['st'], [sub['strasse'] for sub in streets_by_city], scorer=fuzz.token_set_ratio, limit=1) if sub[1]>=85]
				else:
					messages.info(self.request, "Die gefundene Strasse existiert noch nicht. Wenn Sie sie anlegen wollen, bitte 'Ort und Strasse anlegen' anhaken.")
					self.request.session['city_create'] = True
					return HttpResponseRedirect(self.success_url+url_args(self.request))
			else:
				messages.info(self.request, "Die gefundene Strasse existiert noch nicht, aber Sie haben keine Berechtigung um Strassen anzulegen!")
				return HttpResponseRedirect(self.success_url+url_args(self.request))
		matching_street = list(Strassen.objects.values('strasse','ort','id').filter(ort_id__in=[sub['id'] for sub in matching_cities],strasse__in=filtered_street_names))

		matching_category = process.extract(result['na'], [sub[0] for sub in DIENSTLEISTER_AUSWAHL], limit=1)
		category = matching_category[0][0] if matching_category[0][1] > 85 else ''

		if filtered_street_names:
			existing_clients = list(Klienten.objects.values('name','id').filter(ort=matching_street[0]['ort'],strasse=matching_street[0]['id']))
			if existing_clients:
				for client in existing_clients:
					if process.extractOne(result['na'],client, scorer=fuzz.token_set_ratio)[1] > 95 and not force_create:
						existing_client = Klienten.objects.get(id=client['id'])
						messages.info(self.request, 'Ein ähnlich oder gleich lautender Dienstleister existiert bereits: "<a href="'+self.success_url+str(existing_client.id)+'/">'+existing_client.name+'</a>" ')
						self.request.session['force_create'] = True
						return HttpResponseRedirect(self.success_url+url_args(self.request))

		klient = Klienten(
			name = result['na'],
			ort  = Orte.objects.get(id=matching_street[0]['ort']),
			strasse = Strassen.objects.get(id=matching_street[0]['id']),
			hausnr = result['hn'],
			telefon = result['ph'],
			mobil = result['mph'],
			typ = 'D',
			created_by = self.request.user,
			kategorie = category,
		)
		klient.save()
		messages.success(self.request, 'Dienstleister "<a href="'+self.success_url+str(klient.id)+'/">'+klient.name+'</a>" wurde erfolgreich hinzugefügt.')
		# clear search criteria
		self.request.session.pop('suchname')
		self.request.session.pop('suchort')
		return HttpResponseRedirect(self.this_url+url_args(self.request))
