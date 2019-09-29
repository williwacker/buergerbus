from django.template import loader, Context
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from trml2pdf import trml2pdf
from django.core.mail import EmailMessage

from .tables import FahrtagTable, BuerotagTable, TourTable, FahrerTable
from .filters import FahrtagFilter, BuerotagFilter
from .utils import FahrtageSchreiben, BuerotageSchreiben
from .forms import FahrtagChgForm, BuerotagChgForm, FahrplanEmailForm
from .models import Fahrtag, Buerotag
from Tour.models import Tour
from Team.models import Fahrer, Koordinator
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list, get_buero_list
from Basis.utils import get_sidebar, has_perm, url_args
from Basis.views import MyListView, MyDetailView, MyView

class FahrplanView(MyListView):
	permission_required = 'Tour.view_tour'

	def get_queryset(self):
		return TourTable(Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id']))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		ft = Fahrtag.objects.filter(pk=self.kwargs['id'])
		context['pre_table'] = FahrerTable(ft)
		context['title'] = 'Fahrplan {} am {}'.format(ft.first().team,ft.first())
		return context

class FahrplanAsPDF(MyView):
	permission_required = 'Tour.view_tour'

	def pdf_render_to_response(self,template_src, context_dict={}, filename=None, prompt=False):
		response = HttpResponse(content_type='application/pdf')
		if not filename:
			filename = template+'.pdf'
		cd = []
		if prompt:
			cd.append('attachment')
		cd.append('filename=%s' % filename)
		template = loader.get_template(template_src)
#		context_dict['filename'] = filename
		rml = template.render(context_dict)
		return trml2pdf.parseString(rml)
		
	def get(self, request, id):
		fahrtag_liste = Fahrtag.objects.get(pk=id)
		tour_liste = Tour.objects.order_by('uhrzeit').filter(datum=id)
		context = {'fahrtag_liste':fahrtag_liste,'tour_liste':tour_liste}
		filename = 'Buergerbus_Fahrplan_{}_{}.pdf'.format(str(fahrtag_liste.team).replace(' ','_'), fahrtag_liste.datum)
		pdf = self.pdf_render_to_response('Einsatztage/tour_as_pdf.rml', context, filename)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			content = "inline; filename='%s'" %(filename)
			path = settings.TOUR_PATH + filename
			with open(path, 'wb') as f:
				f.write(response.content)
			return response
		return HttpResponse("Kein Dokument vorhanden")

class FahrplanEmailView(MyDetailView):
	form_class = FahrplanEmailForm
	permission_required = 'Tour.view_tour'
	success_url = '/Einsatztage/fahrer/'
	context = {}

	def get_context_data(self):
#		context = {}
		self.context['sidebar_liste'] = get_sidebar(self.request.user)
		ft = Fahrtag.objects.get(pk=self.kwargs['id'])
		self.context['fahrtag_liste'] = ft
		self.context['tour_liste'] = Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id'])
		self.context['title'] = 'Fahrplan {} am {} versenden'.format(ft.team,ft.datum)
		self.context['submit_button'] = "Senden"
		self.context['back_button'] = "Abbrechen"
		self.context['url_args'] = url_args(self.request)
		# Fahrplan Dateiname
		self.context['filename'] = 'Buergerbus_Fahrplan_{}_{}.pdf'.format(str(self.context['fahrtag_liste'].team).replace(' ','_'), self.context['fahrtag_liste'].datum)
		self.context['filepath'] = [settings.TOUR_PATH+self.context['filename']]
#		return context

	def get_dsgvo_klienten(self, context):
		klienten_liste = {}
		for tour in context['tour_liste']:
			if tour.klient.dsgvo == '01':
				klienten_liste[tour.klient.name] = tour.klient
		return klienten_liste

	def writeDSGVO(self, klienten_liste):
		filepath_liste = []
		for key in klienten_liste:
			self.context['klient'] = klienten_liste[key]
			filename = "DSGVO_{}_{}.pdf".format(klienten_liste[key].nachname, klienten_liste[key].vorname)
			pdf = FahrplanAsPDF().pdf_render_to_response('Klienten/dsgvo.rml', self.context, filename)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				content = "inline; filename='%s'" %(filename)
				filepath = settings.DSGVO_PATH + filename
				filepath_liste.append(filepath)
				with open(filepath, 'wb') as f:
					f.write(response.content)
		return filepath_liste
	
	def get(self, request, *args, **kwargs):
		self.get_context_data()
		if settings.SEND_DSGVO:
			klienten_liste = self.get_dsgvo_klienten(self.context)
			# DSGVO Dateinamen
			filepath_liste = self.writeDSGVO(klienten_liste)
			self.context['filepath']+=filepath_liste
		pdf = FahrplanAsPDF().pdf_render_to_response('Einsatztage/tour_as_pdf.rml', self.context, self.context['filename'])
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			content = "inline; filename='%s'" %(self.context['filename'])
			path = settings.TOUR_PATH + self.context['filename'][0]
			with open(path, 'wb') as f:
				f.write(response.content)
		form = self.form_class(initial=self.initial)
		self.initial['von'] = settings.EMAIL_HOST_USER
		ft = self.context['fahrtag_liste']
		email_to = []
		if ft.fahrer_vormittag:
			email_to.append(ft.fahrer_vormittag.email)
		if ft.fahrer_nachmittag:
			email_to.append(ft.fahrer_nachmittag.email)
		if ft.team.email:
			email_to.append(ft.team.email)	
		self.initial['an'] = "; ".join(email_to)
		self.initial['betreff'] = '[Bürgerbus] Fahrplan {} am {}'.format(ft.team,ft.datum)
		self.initial['datei'] = '\n'.join(self.context['filepath'])
		self.context['form'] = form
		return render(request, self.template_name, self.context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		self.context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			email = EmailMessage(
				post['betreff'],
				post['text'],
				post['von'],
				post['an'].split(";"),
				reply_to=post['von'].split(";"),
			)
			if post['cc']:
				email.cc = post['cc'].split(";")
			for filepath in self.context['filepath']:
				email.attach_file(filepath)
			email.send(fail_silently=False)
			if settings.SEND_DSGVO:
				# klienten dsgvo auf 'versandt' stellen
				klienten_liste = self.get_dsgvo_klienten(self.context)
				for key in klienten_liste:
					klienten_liste[key].dsgvo = '02'
					klienten_liste[key].save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, post['betreff']+' wurde erfolgreich versandt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)			
		return render(request, self.template_name, self.context)

class FahrtageListView(MyListView):
	permission_required = 'Einsatztage.view_fahrtag'

	def get_queryset(self):
		FahrtageSchreiben(self.request.user)
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = Fahrtag.objects.order_by('datum','team').filter(archiv=False, team__in=get_bus_list(self.request))
		if team:
			qs = qs.filter(team=team)
		if sort:
			qs = qs.order_by(sort)
		table = FahrtagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrtage"
		context['filter'] = FahrtagFilter(self.request.GET, queryset=Fahrtag.objects.filter(archiv=False, team__in=get_bus_list(self.request)))
		context['url_args'] = url_args(self.request)
		return context

class FahrtageChangeView(MyDetailView):
	form_class = FahrtagChgForm
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrereinsatz ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(instance=Fahrtag.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			fahrtag = Fahrtag.objects.get(pk=kwargs['pk'])
			if post['fahrer_vormittag'] != "":
				fahrtag.fahrer_vormittag=Fahrer.objects.get(pk=int(post['fahrer_vormittag']))
			else:
				fahrtag.fahrer_vormittag=None
			if post['fahrer_nachmittag'] != "":
				fahrtag.fahrer_nachmittag=Fahrer.objects.get(pk=int(post['fahrer_nachmittag']))
			else:
				fahrtag.fahrer_nachmittag=None
			fahrtag.updated_by = request.user
			fahrtag.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Fahrtag "<a href="'+request.path+url_args(request)+'">'+str(fahrtag.datum)+' '+str(fahrtag.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)			
		return render(request, self.template_name, context)		

class BuerotageListView(MyListView):
	permission_required = 'Einsatztage.view_buerotag'
	
	def get_queryset(self):
		BuerotageSchreiben(self.request.user)
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = Buerotag.objects.order_by('team','datum').filter(archiv=False, team__in=get_buero_list(self.request))
		if team:
			qs = qs.filter(team=team)
		if sort:
			qs = qs.order_by(sort)
		table = BuerotagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bürotage"
		context['filter'] = BuerotagFilter(self.request.GET, queryset=Buerotag.objects.filter(archiv=False, team__in=get_buero_list(self.request)))
		context['url_args'] = url_args(self.request)
		return context

class BuerotageChangeView(MyDetailView):
	form_class = BuerotagChgForm
	permission_required = 'Einsatztage.change_buerotag'
	success_url = '/Einsatztage/buero/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Bürotag ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		context['url_args'] = url_args(self.request)
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Buerotag.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		context['form'] = form
		if form.is_valid():
			post = request.POST.dict()
			buero = Buerotag.objects.get(pk=kwargs['pk'])
			if post['koordinator'] != "":
				buero.mitarbeiter=Koordinator.objects.get(pk=int(post['koordinator']))
			buero.updated_by = request.user
			buero.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Bürotag "<a href="'+request.path+url_args(request)+'">'+str(buero.datum)+' '+str(buero.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)

		return render(request, self.template_name, context)		
