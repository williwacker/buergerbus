from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.http import (FileResponse, Http404, HttpResponse,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from trml2pdf import trml2pdf

from Basis.utils import get_sidebar, url_args
from Basis.views import MyDetailView, MyListView, MyUpdateView, MyView
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_buero_list, get_bus_list
from Klienten.models import Klienten
from Team.models import Fahrer, Koordinator
from Tour.models import Tour

from .filters import BuerotagFilter, FahrtagFilter
from .forms import BuerotagChgForm, FahrplanEmailForm, FahrtagChgForm
from .models import Buerotag, Fahrtag
from .tables import BuerotagTable, FahrerTable, FahrtagTable, TourTable
from .utils import BuerotageSchreiben, FahrplanBackup, FahrtageSchreiben


class FahrplanView(MyListView):
	permission_required = 'Tour.view_tour'
	success_url = '/Einsatztage/fahrer/'

	def get_queryset(self):
		return TourTable(Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id']))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		ft = Fahrtag.objects.filter(pk=self.kwargs['id'])
		context['pre_table'] = FahrerTable(ft)
		context['title'] = 'Fahrplan {} am {}'.format(ft.first().team,ft.first())
		context['back_button'] = ["Zurück",self.success_url+url_args(self.request)]
		return context

class FahrplanAsPDF(MyView):
	permission_required = 'Tour.view_tour'
	success_url = '/Einsatztage/fahrer/'

	def pdf_render_to_response(self, template_src, context_dict={}, filename=None, prompt=False):
		context_dict['filename'] = filename
		template = get_template(template_src)
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
			filepath = settings.TOUR_PATH + filename
			try:
				with open(filepath, 'wb') as f:
					f.write(response.content)
				f.close()
				response = FileResponse(open(filepath, 'rb'), content_type="application/pdf")
				response["Content-Disposition"] = "filename={}".format(filename)
				return response
			except:
				messages.error(request, 'Dokument <b>'+filename+'</b> ist noch geöffnet.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		return HttpResponse("Kein Dokument vorhanden")

class FahrplanAsCSV(MyView):
	permission_required = 'Tour.view_tour'
	success_url = '/Einsatztage/fahrer/'

	def get(self, request, id):
		FahrplanBackup().export_as_csv(id)
		return HttpResponseRedirect(self.success_url+url_args(request))

class FahrplanBackupView(MyView):
	permission_required = 'Tour.view_tour'
	success_url = '/Einsatztage/fahrer/'

	def get(self, request):
		FahrplanBackup().send_backup()
		return HttpResponseRedirect(self.success_url+url_args(request))		

class FahrplanEmailView(MyDetailView):
	form_class = FahrplanEmailForm
	permission_required = 'Tour.view_tour'
	success_url = '/Einsatztage/fahrer/'
	context = {}

	def get_context_data(self):
		self.context['sidebar_liste'] = get_sidebar(self.request.user)
		ft = Fahrtag.objects.get(pk=self.kwargs['id'])
		self.context['fahrtag_liste'] = ft
		self.context['tour_liste'] = Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id'])
		self.context['title'] = 'Fahrplan {} am {} versenden'.format(ft.team,ft.datum)
		self.context['submit_button'] = "Senden"
		self.context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		self.context['url_args'] = url_args(self.request)
		self.context['filepath'] = []

	def get_dsgvo_klienten(self):
		klienten_liste = {}
		for tour in self.context['tour_liste']:
			if tour.klient.dsgvo == '01': klienten_liste[tour.klient.name] = tour.klient
		return klienten_liste

	def writeDSGVO(self):
		filepath_liste = []
		if settings.SEND_DSGVO:
			klienten_liste = self.get_dsgvo_klienten()
			klienten_keys = []
			for key in klienten_liste:
				klienten_keys.append(klienten_liste[key].id)
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
					f.close()
			self.request.session['klienten_keys'] = klienten_keys
		return filepath_liste

	def writeFahrplan(self):
		filename = 'Buergerbus_Fahrplan_{}_{}.pdf'.format(str(self.context['fahrtag_liste'].team).replace(' ','_'), self.context['fahrtag_liste'].datum)
		pdf = FahrplanAsPDF().pdf_render_to_response('Einsatztage/tour_as_pdf.rml', self.context, filename)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			content = "inline; filename='%s'" %(filename)
			filepath = settings.TOUR_PATH + filename
			try:
				with open(filepath, 'wb') as f:
					f.write(response.content)
				f.close()
			except:
				messages.error(self.request, 'Dokument <b>'+filepath+'</b> ist noch geöffnet und kann nicht geschrieben werden.')
		return [filepath]

	def get(self, request, *args, **kwargs):
		self.get_context_data()
		self.context['filepath']+=self.writeDSGVO()
		self.context['filepath']+=self.writeFahrplan()
		form = self.form_class(initial=self.initial)
		self.initial['von'] = settings.EMAIL_HOST_USER
		ft = self.context['fahrtag_liste']
		email_to = []
		if ft.fahrer_vormittag: email_to.append(ft.fahrer_vormittag.email)
		if ft.fahrer_nachmittag: email_to.append(ft.fahrer_nachmittag.email)
		if ft.team.email: email_to.append(ft.team.email)	
		self.initial['an'] = "; ".join(email_to)
		self.initial['betreff'] = '[Bürgerbus] Fahrplan {} am {}'.format(ft.team,ft.datum)
		self.initial['datei'] = '\n'.join(self.context['filepath'])
		self.context['form'] = form
		return render(request, self.template_name, self.context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		self.context['form'] = form
		if form.is_valid():
			post = form.cleaned_data
			email = EmailMessage(
				post['betreff'],
				post['text'],
				post['von'],
				post['an'].split(";"),
				reply_to=post['von'].split(";"),
			)
			if post['cc']: email.cc = post['cc'].split(";")
			for filepath in post['datei'].split('\n'):
				email.attach_file(filepath.strip('\r'))
			email.send(fail_silently=False)
			if settings.SEND_DSGVO:
				# klienten dsgvo auf 'versandt' stellen
				klienten_keys = self.request.session.pop('klienten_keys',[])
				for id in klienten_keys:
					klient = Klienten.objects.get(id=id)
					klient.dsgvo = '02'
					klient.save(force_update=True)
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
		if self.request.user.has_perm('Einsatztage.change_fahrtag'): FahrtageSchreiben()
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = Fahrtag.objects.order_by('datum','team').filter(archiv=False, team__in=get_bus_list(self.request))
		if team: qs = qs.filter(team=team)
		if sort: qs = qs.order_by(sort)
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

class FahrtageChangeView(MyUpdateView):
	form_class = FahrtagChgForm
	permission_required = 'Einsatztage.change_fahrtag'
	success_url = '/Einsatztage/fahrer/'
	model = Fahrtag
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrereinsatz ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
		return super(FahrtageChangeView, self).form_valid(form)	

### Bürotage

class BuerotageListView(MyListView):
	permission_required = 'Einsatztage.view_buerotag'
	
	def get_queryset(self):
		if self.request.user.has_perm('Einsatztage.change_buerotag'): BuerotageSchreiben()
		team = self.request.GET.get('team')
		sort = self.request.GET.get('sort')
		qs = Buerotag.objects.order_by('team','datum').filter(archiv=False, team__in=get_buero_list(self.request))
		if team: qs = qs.filter(team=team)
		if sort: qs = qs.order_by(sort)
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

class BuerotageChangeView(MyUpdateView):
	form_class = BuerotagChgForm
	permission_required = 'Einsatztage.change_buerotag'
	success_url = '/Einsatztage/buero/'
	model = Buerotag

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bürotag ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
		return super(BuerotageChangeView, self).form_valid(form)	
