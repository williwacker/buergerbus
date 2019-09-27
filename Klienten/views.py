from django import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib import messages
from jet.filters import RelatedFieldAjaxListFilter
from .forms import FahrgastAddForm, FahrgastChgForm, DienstleisterAddForm, DienstleisterChgForm
from .forms import OrtAddForm, OrtChgForm
from .forms import StrassenAddForm, StrassenChgForm
from .models import Klienten, Orte, Strassen
from .tables import OrteTable, StrassenTable, DienstleisterTable, FahrgaesteTable
from .filters import StrassenFilter, OrteFilter, FahrgaesteFilter, DienstleisterFilter
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Basis.utils import get_sidebar, render_to_pdf, has_perm, url_args
from Basis.views import MyListView, MyDetailView, MyView

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
		if has_perm(self.request.user, 'Klienten.add_klienten'):
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

class FahrgastChangeView(MyDetailView):
	form_class = FahrgastChgForm
	permission_required = 'Klienten.change_klienten'
	success_url = '/Klienten/fahrgaeste/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast ändern"
		if has_perm(self.request.user, 'Klienten.delete_klienten'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(request)
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
		context['form'] = form
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
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Fahrgast "<a href="'+request.path+url_args(request)+'">'+klient.name+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)		

class FahrgastDeleteView(MyView):
	permission_required = 'Klienten.delete_klienten'
	success_url = '/Klienten/fahrgaeste/'

	def get(self, request, *args, **kwargs):
		k = Klienten.objects.get(pk=kwargs['pk'])
		k.delete()
		messages.success(request, 'Fahrgast '+k.name+' wurde gelöscht.')
		return HttpResponseRedirect(self.success_url+url_args(request))

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

from Einsatztage.views import FahrplanAsPDF

class DSGVOasPDFView(MyView):
	permission_required = 'Klienten.view_klienten'

	def get(self, request, id):
		klient = Klienten.objects.get(pk=id)
		context = {'klient':klient}
		filename = "DSGVO_{}_{}.pdf".format(klient.nachname, klient.vorname)
		pdf = FahrplanAsPDF().pdf_render_to_response('Klienten/dsgvo.rml', context, filename)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			content = "inline; filename='%s'" %(filename)
			filepath = settings.DSGVO_PATH + filename
			with open(filepath, 'wb') as f:
				f.write(response.content)
			return response
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
		if has_perm(self.request.user, 'Klienten.add_klienten'):
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
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)		
		return render(request, self.template_name, context)

class DienstleisterChangeView(MyDetailView):
	form_class = DienstleisterChgForm
	permission_required = 'Klienten.change_klienten'
	success_url = '/Klienten/dienstleister/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Fahrgast ändern"
		if has_perm(self.request.user, 'Klienten.delete_klienten'):
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

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
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
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Dienstleister "<a href="'+request.path+url_args(request)+'">'+klient.name+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)		

class DienstleisterDeleteView(MyView):
	permission_required = 'Klienten.delete_klienten'
	success_url = '/Klienten/dienstleister/'

	def get(self, request, *args, **kwargs):
		k = Klienten.objects.get(pk=kwargs['pk'])
		k.delete()
		messages.success(request, 'Dienstleister '+k.name+' wurde gelöscht.')
		return HttpResponseRedirect(self.success_url+url_args(request))	

class OrtView(MyListView):
	permission_required = 'Klienten.view_orte'
	
	def get_queryset(self):
		ort = self.request.GET.get('ort')
		bus = self.request.GET.get('bus')
		qs = Orte.objects.order_by('bus','ort')
		if ort:
			qs = qs.filter(ort=ort)
		if bus:
			qs = qs.filter(bus=bus)
		return OrteTable(qs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Orte"
		if has_perm(self.request.user, 'Klienten.add_orte'):
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

class OrtChangeView(MyDetailView):
	form_class = OrtChgForm
	permission_required = 'Klienten.change_orte'
	success_url = '/Klienten/orte/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Ort ändern"
		if has_perm(self.request.user, 'Klienten.delete_orte'):
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

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			ort = Orte.objects.get(pk=kwargs['pk'])
			if post['bus']:
				ort.bus=Bus.objects.get(pk=int(post['bus']))
			ort.updated_by = request.user
			ort.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Ort "<a href="'+request.path+url_args(request)+'">'+ort.ort+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)		

class OrtDeleteView(MyView):
	permission_required = 'Klienten.delete_orte'
	success_url = '/Klienten/orte/'

	def get(self, request, *args, **kwargs):
		ort = Orte.objects.get(pk=kwargs['pk'])
		ort.delete()
		messages.success(request, 'Ort '+str(ort)+' wurde gelöscht.')
		return HttpResponseRedirect(self.success_url+url_args(request))	

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
		if has_perm(self.request.user, 'Klienten.add_strassen'):
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

class StrassenChangeView(MyDetailView):
	form_class = StrassenChgForm
	permission_required = 'Klienten.change_strassen'
	success_url = '/Klienten/strassen/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Strasse ändern"
		if has_perm(self.request.user, 'Klienten.delete_strassen'):
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

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			strasse = Strassen.objects.get(pk=kwargs['pk'])
			strasse.strasse=post['strasse']
			strasse.updated_by = request.user
			strasse.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Strasse "<a href="'+request.path+url_args(request)+'">'+strasse.strasse+' in '+str(strasse.ort)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)
		return render(request, self.template_name, context)		

class StrassenDeleteView(MyView):
	permission_required = 'Klienten.delete_strassen'
	success_url = '/Klienten/strassen/'

	def get(self, request, *args, **kwargs):
		strasse = Strassen.objects.get(pk=kwargs['pk'])
		strasse.delete()
		messages.success(request, 'Strasse '+strasse.strasse+' in '+str(strasse.ort)+' wurde gelöscht.')
		return HttpResponseRedirect(self.success_url+url_args(request))	
