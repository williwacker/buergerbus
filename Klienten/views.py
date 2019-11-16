import subprocess
from fuzzywuzzy import fuzz, process
from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from django import forms
from .forms import FahrgastAddForm, FahrgastChgForm, DienstleisterAddForm, DienstleisterChgForm, KlientenSearchForm, KlientenSearchResultForm
from .forms import OrtAddForm, OrtChgForm
from .forms import StrassenAddForm, StrassenChgForm
from .models import Klienten, Orte, Strassen, DIENSTLEISTER_AUSWAHL
from .tables import OrteTable, StrassenTable, DienstleisterTable, FahrgaesteTable
from .filters import StrassenFilter, OrteFilter, FahrgaesteFilter, DienstleisterFilter
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf, url_args, del_message
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView, MyDeleteView, MyMultiFormsView
from Einsatztage.views import FahrplanAsPDF
from Basis.telefonbuch_suche import Telefonbuch

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

class FahrgastAddView(MyDetailView):
	form_class = FahrgastAddForm
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/fahrgaeste/'

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
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
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
			storage = messages.get_messages(request)
			storage.used = True	
			messages.success(request, 'Fahrgast "<a href="'+self.success_url+str(klient.id)+'/'+url_args(request)+'">'+klient.name+'</a>" wurde erfolgreich hinzugefügt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)

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
		context['back_button'] = "Abbrechen"
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
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		if instance.ort.bus != None:
			instance.bus=instance.ort.bus
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_url += url_args(self.request)
		self.success_message = 'Fahrgast "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich geändert.'
		return super(FahrgastChangeView, self).form_valid(form)	

class FahrgastDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_klienten'
	success_url = '/Klienten/fahrgaeste/'
	model = Klienten
	pass

class DSGVOView(MyDetailView):
	permission_required = 'Klienten.view_klienten'

	template_name = 'Klienten/dsgvo.html'
	context_object_name = 'klient'

	def get_queryset(self):
		return Klienten.objects.filter(pk=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "DSGVO anzeigen"
		context['back_button'] = "Zurück"
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
				messages.success(request, 'Dokument <b>'+filepath+'</b> wurde erstellt.')
			except:
				messages.error(request, 'Dokument <b>'+filepath+'</b> ist noch geöffnet.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		return HttpResponse("Kein Dokument vorhanden")		

class DienstleisterView(MyListView):
	permission_required = 'Klienten.view_klienten'

	def get_queryset(self):
		name = self.request.GET.get('name')
		ort = self.request.GET.get('ort')
		kategorie = self.request.GET.get('kategorie')
		sort = self.request.GET.get('sort')
		qs = Klienten.objects.order_by('name','ort').filter(typ='D')
		if ort:
			qs = qs.filter(ort=ort)
		if name:
			qs = qs.filter(name=name)
		if kategorie:
			qs = qs.filter(kategorie=kategorie)
		if sort:
			qs = qs.order_by(sort)
		return DienstleisterTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dienstleister"
		if self.request.user.has_perm('Klienten.add_klienten'):
			context['add'] = "Dienstleister"
		context['filter'] = DienstleisterFilter(self.request.GET, queryset=Klienten.objects.order_by('name','ort').filter(typ='D'))
		context['url_args'] = url_args(self.request)
		return context		

class DienstleisterAddView(MyDetailView):
	form_class = DienstleisterAddForm
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/dienstleister/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Dienstleister hinzufügen"
		context['submit_button'] = "Sichern"
		if self.request.GET.get('_popup') == '1':
			context['popup'] = '1'
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
		context['form'] = form
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
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Dienstleister "<a href="'+self.success_url+str(klient.id)+'/'+url_args(request)+'">'+klient.name+'</a>" wurde erfolgreich hinzugefügt.')
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

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast ändern"
		if self.request.user.has_perm('Klienten.delete_klienten'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Klienten.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_url += url_args(self.request)
		self.success_message = 'Dienstleister "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich geändert.'
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
		context['back_button'] = ["Abbrechen",self.success_url]
		if self.request.GET.get('_popup') == '1':
			context['popup'] = '1'
		return context

	def get_suchen_initial(self):
		name = self.request.GET.get('name')
		ort  = self.request.GET.get('ort')
		popup = self.request.GET.get('_popup')
		return {'name':name, 'ort':ort, '_popup':popup}

	def get_anlegen_initial(self):
		name = self.request.GET.get('name')
		ort  = self.request.GET.get('ort')
		result_list = ['initial']
		if name:
			result_list = Telefonbuch().dastelefonbuch(name,ort,'D')
		return {'suchergebnis':result_list}
	
	def create_anlegen_form(self, initial, prefix, data=None, files=None):
		form = self.form_classes['anlegen'](self.request.POST)
		form.fields['suchergebnis'] = forms.ChoiceField(required=True, widget=forms.RadioSelect(), choices = [])
		del_message(self.request)
		choices = []
		result_list = initial['suchergebnis']
		if not result_list:
			messages.error(self.request, 'Keinen Namen anhand der Suchkriterien gefunden')
		elif result_list[0] != 'initial':
			messages.success(self.request, 'Die folgenden Namen wurden gefunden:')
			for i in range(len(result_list)):
				# na = Name, pc = PLZ, ci = City, st = Street, hn = house-no, ph = phone, mph = mobile phone
				choices.append((i+1,'{} {} {} {} {}'.format(result_list[i]['na'],result_list[i]['pc'],result_list[i]['ci'],result_list[i]['st'],result_list[i]['hn'])))
		choices.append((0,'Adresse manuell eingeben'))
		form.fields['suchergebnis'].choices = choices
		self.request.session['clientsearch_results'] = result_list
		return form

	def suchen_form_valid(self, form):
		popup = '&_popup='+self.request.GET.get('_popup') if self.request.GET.get('_popup') else ''
		return HttpResponseRedirect(self.this_url+'?name='+form.cleaned_data['name']+'&ort='+form.cleaned_data['ort']+popup)	

	def anlegen_form_valid(self, form):
		if form.cleaned_data['suchergebnis'] == '0':
			del_message(self.request)
			messages.success(self.request, 'Bitte den Dienstleister manuell eingeben')
			return HttpResponseRedirect(self.manual_url+url_args(self.request))
		choice  = int(form.cleaned_data['suchergebnis'])
		self.request.session['clientsearch_choice'] = choice
		result = self.request.session.pop('clientsearch_results',[])[choice-1]
		self.create_dienstleister(result,force_create=form.cleaned_data['force_create'], city_create=form.cleaned_data['city_create'])
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
					messages.error(self.request, "Der gefundene Ort existiert noch nicht. Wenn Sie ihn anlegen wollen, bitte 'Ort und Strasse anlegen' anhaken.")
					return HttpResponseRedirect(self.success_url)
			else:
				messages.error(self.request, "Der gefundene Ort existiert noch nicht, aber Sie haben keine Berechtigung um Orte anzulegen!")
				return HttpResponseRedirect(self.success_url)
		best_match = process.extract(result['ci'], [sub['ort'] for sub in cities_by_zip], scorer=fuzz.token_set_ratio, limit=100)  # for debugging only
		filtered_city_names = [sub[0] for sub in process.extract(result['ci'], [sub['ort'] for sub in cities_by_zip], scorer=fuzz.token_set_ratio, limit=100) if sub[1]>=85]
		matching_cities = list(Orte.objects.values('ort','id').filter(ort__in=filtered_city_names))

		streets_by_city = list(Strassen.objects.values('strasse','ort','id').filter(ort_id__in=[sub['id'] for sub in matching_cities]))
		filtered_street_names = [sub[0] for sub in process.extract(result['st'], [sub['strasse'] for sub in streets_by_city], scorer=fuzz.token_set_ratio, limit=1) if sub[1]>=85]
		if not filtered_street_names:
			if self.request.user.has_perm('Klienten.add_strassen'):
				self.create_strasse(strasse=result['st'], ort=result['ci'])
				streets_by_city = list(Strassen.objects.values('strasse','ort','id').filter(ort_id__in=[sub['id'] for sub in matching_cities]))
				filtered_street_names = [sub[0] for sub in process.extract(result['st'], [sub['strasse'] for sub in streets_by_city], scorer=fuzz.token_set_ratio, limit=1) if sub[1]>=85]
			else:
				messages.error(self.request, "Die gefundene Strasse existiert noch nicht, aber Sie haben keine Berechtigung um Strassen anzulegen!")
				return HttpResponseRedirect(self.success_url)
		matching_street = list(Strassen.objects.values('strasse','ort','id').filter(ort_id__in=[sub['id'] for sub in matching_cities],strasse__in=filtered_street_names))

		matching_category = process.extract(result['na'], [sub[0] for sub in DIENSTLEISTER_AUSWAHL], limit=1)
		category = matching_category[0][0] if matching_category[0][1] > 85 else ''

		if filtered_street_names:
			existing_clients = list(Klienten.objects.values('name','id').filter(ort=matching_street[0]['ort'],strasse=matching_street[0]['id']))
			if existing_clients:
				matching_client = process.extractOne(result['na'],[sub['name'] for sub in existing_clients], scorer=fuzz.token_set_ratio)
				if matching_client[1] > 95 and not force_create:
					existing_client = Klienten.objects.get(name=matching_client[0])
					del_message(self.request)
					messages.error(self.request, 'Ein ähnlich lautender Dienstleister existiert bereits: "<a href="'+self.success_url+str(existing_client.id)+'/">'+existing_client.name+'</a>" ')
					return HttpResponseRedirect(self.success_url)

		klient = Klienten(
			name = result['na'],
			ort  = Orte.objects.get(id=matching_street[0]['ort']),
			strasse = Strassen.objects.get(id=matching_street[0]['id']),
			hausnr = result['hn'],
			telefon = result['ph'],
			mobil = result['mph'],
			typ = 'D',
			dsgvo = '99',
			updated_by = self.request.user,
			kategorie = category,
		)
		klient.save()
		messages.success(self.request, 'Dienstleister "<a href="'+self.success_url+str(klient.id)+'/">'+klient.name+'</a>" wurde erfolgreich hinzugefügt.')
		return HttpResponseRedirect(self.this_url)

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

class OrtAddView(MyDetailView):
	form_class = OrtAddForm
	permission_required = 'Klienten.add_orte'
	success_url = '/Klienten/orte/'

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
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			ort = Orte(	
				ort=post['ort'],
				updated_by = request.user
				)
			if post['bus']:
				ort.bus=Bus.objects.get(pk=int(post['bus']))
			
			ort.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Ort "<a href="'+self.success_url+str(ort.id)+'/'+url_args(request)+'">'+str(ort)+'</a>" wurde erfolgreich hinzugefügt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)

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
		context['back_button'] = "Abbrechen"
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
		self.success_url += url_args(self.request)
		self.success_message = 'Ort "<a href="'+self.success_url+str(instance.id)+'">'+instance.ort+'</a>" wurde erfolgreich geändert.'
		return super(OrtChangeView, self).form_valid(form)	

class OrtDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_orte'
	success_url = '/Klienten/orte/'
	model = Orte
	pass

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

class StrassenAddView(MyDetailView):
	form_class = StrassenAddForm
	permission_required = 'Klienten.add_strassen'
	success_url = '/Klienten/strassen/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Strasse hinzufügen"
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
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			o = Orte.objects.get(pk=int(post['ort']))
			strasse = Strassen(	ort=o,
							strasse=post['strasse'],
							updated_by = request.user
					)
			strasse.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Strasse "<a href="'+self.success_url+str(strasse.id)+'/'+url_args(request)+'">'+strasse.strasse+' in '+str(strasse.ort)+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)	

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
		context['back_button'] = "Abbrechen"
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
		self.success_url += url_args(self.request)
		self.success_message = 'Strasse "<a href="'+self.success_url+str(instance.id)+'">'+instance.strasse+'</a>" wurde erfolgreich geändert.'
		return super(StrassenChangeView, self).form_valid(form)			

class StrassenDeleteView(MyDeleteView):
	permission_required = 'Klienten.delete_strassen'
	success_url = '/Klienten/strassen/'
	model = Strassen
	pass