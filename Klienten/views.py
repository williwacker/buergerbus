import subprocess
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
from .models import Klienten, Orte, Strassen
from .tables import OrteTable, StrassenTable, DienstleisterTable, FahrgaesteTable
from .filters import StrassenFilter, OrteFilter, FahrgaesteFilter, DienstleisterFilter
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf, url_args, del_message
from Basis.views import MyListView, MyDetailView, MyView, MyUpdateView, MyDeleteView
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
				return HttpResponse('''<script type="text/javascript">opener.location.reload(false);opener.dismissAddAnotherPopup(window);</script>''')
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

class DienstleisterSearchView(MyDetailView):
	form_class = KlientenSearchForm
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/dienstleister/add/searchresult/'
	fail_url    = '/Klienten/dienstleister/add/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Dienstleister suchen und hinzufügen"
		context['submit_button'] = "Suchen"
		context['back_button'] = "Abbrechen"
		return context

	def get(self, request, *args, **kwargs):
		name = self.request.GET.get('name')
		ort  = self.request.GET.get('ort')
		context = self.get_context_data(request)
		if ort:
			orte = Orte.objects.get(ort=ort)
			form = self.form_class(initial={'name':name, 'ort':orte.pk})
		else:
			name = ''
			form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = form.cleaned_data
			typ = ''
			if 'typ' in post:
				typ = ''.join(post['typ'])
			result_list = Telefonbuch().dastelefonbuch(post['name'],post['ort'].ort,typ)
			if result_list:
				return HttpResponseRedirect(self.success_url+'?name='+post['name']+'&ort='+post['ort'].ort)
			else:
				messages.error(request, 'Keinen Namen anhand der Suchkriterien gefunden')
				return HttpResponseRedirect(self.fail_url+'?name='+post['name']+'&ort='+post['ort'].ort)
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)

class DienstleisterSearchResultView(MyDetailView):
	form_class = KlientenSearchResultForm
	permission_required = 'Klienten.add_klienten'
	success_url = '/Klienten/dienstleister/'
	fail_url = '/Klienten/dienstleister/add/searchresult/'
	manual_url = '/Klienten/dienstleister/add/manual/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Dienstleister suchen und hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Zurück"
		return context

	def get(self, request, *args, **kwargs):
		name = self.request.GET.get('name')
		ort  = self.request.GET.get('ort')
		typ  = self.request.GET.get('typ')
		context = self.get_context_data(request)
		result_list = Telefonbuch().dastelefonbuch(name,ort,typ)
		choices = []
		if not result_list:
			messages.error(request, 'Keinen Namen anhand der Suchkriterien gefunden')
		else:
			messages.success(request, 'Die folgenden Namen wurden gefunden:')
			for i in range(len(result_list)):
				choices.append((i+1,'{} {} {} {}'.format(result_list[i]['na'],result_list[i]['ci'],result_list[i]['st'],result_list[i]['hn'])))
		choices.append((0,'Adresse manuell eingeben'))
		form = self.form_class(initial=self.initial)
		form.fields['suchergebnis'] = forms.ChoiceField(widget=forms.RadioSelect(), choices = [])
		form.fields['suchergebnis'].choices = choices
#		result_string = str(result_list)
#		form.fields['details'] = result_string
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
		storage = messages.get_messages(self.request)
		storage.used = True
		if form.is_valid():
			post = form.cleaned_data
			if post['suchergebnis'] == '0':
				return HttpResponseRedirect(self.manual_url)
			else:
				index = int(post['suchergebnis'])-1
#				selected_name = result_list[index]
#				o = Orte.objects.get(ort=selected_name['ci'])
			return HttpResponseRedirect(self.success_url)
		else:
			messages.error(request, form.errors)		
		return HttpResponseRedirect(self.fail_url+url_args(request))


class OrtView(MyListView):
	permission_required = 'Klienten.view_orte'
	
	def get_queryset(self):
		ort = self.request.GET.get('ort')
		bus = self.request.GET.get('bus')
		# nur managed orte anzeigen
		qs = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(self.request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
		if ort:
			qs = qs.filter(ort=ort)
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