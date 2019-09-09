from Basis.utils import render_to_pdf
from django.template.loader import get_template
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
#import pdfkit 

from .tables import FahrtagTable, BuerotagTable, TourTable, FahrerTable
from .filters import FahrtagFilter, BuerotagFilter
from .utils import FahrtageSchreiben, BuerotageSchreiben
from .forms import FahrtagChgForm, BuerotagChgForm
from .models import Fahrtag, Buerotag
from Tour.models import Tour
from Team.models import Fahrer, Koordinator
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list, get_buero_list
from Basis.utils import get_sidebar, has_perm
from Basis.views import MyListView, MyDetailView, MyView

class TourView(MyListView):
	auth_name = 'Tour.view_tour'

	def get_queryset(self):
		return TourTable(Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id']))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		ft = Fahrtag.objects.filter(pk=self.kwargs['id'])
		context['pre_table'] = FahrerTable(ft)
		context['title'] = 'Fahrplan {} am {}'.format(ft.first().team,ft.first())
		return context

class GeneratePDF(MyView):
	auth_name = 'Tour.view_tour'

	def get(self, request, id):
		fahrtag_liste = Fahrtag.objects.filter(pk=id).first()
		tour_liste = Tour.objects.order_by('uhrzeit').filter(datum=id)
		context = {'fahrtag_liste':fahrtag_liste,'tour_liste':tour_liste,'skip_nav':1}
#		html = render(request, self.template_name, context)
#		pdfkit.from_string(html, 'out.pdf') 
		pdf = render_to_pdf('Einsatztage/tour_as_pdf.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "Buergerbus_Tour_Bus_%s_%s.pdf" % (fahrtag_liste.team_id, fahrtag_liste.datum)
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Kein Dokument vorhanden")	

class FahrtageListView(MyListView):
	auth_name = 'Einsatztage.view_bus'

	def get_queryset(self):
		FahrtageSchreiben()
		team = self.request.GET.get('team')
		qs = Fahrtag.objects.order_by('datum','team').filter(archiv=False, team__in=get_bus_list(self.request))
		if team:
			qs = qs.filter(team=team)
		table = FahrtagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrtage"
		context['filter'] = FahrtagFilter(self.request.GET, queryset=Fahrtag.objects.filter(archiv=False, team__in=get_bus_list(self.request)))
		return context

class FahrtageChangeView(MyDetailView):
	form_class = FahrtagChgForm
	auth_name = 'Einsatztage.change_bus'
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fahrereinsatz ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(instance=Fahrtag.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST)
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
			messages.success(request, 'Fahrtag "<a href="'+request.path+'">'+str(fahrtag.datum)+' '+str(fahrtag.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Einsatztage/fahrer/')

		return render(request, self.template_name, context)		

class BuerotageListView(MyListView):
	auth_name = 'Einsatztage.view_buero'
	
	def get_queryset(self):
		BuerotageSchreiben()
		team = self.request.GET.get('team')
		qs = Buerotag.objects.order_by('team','datum').filter(archiv=False, team__in=get_buero_list(self.request))
		if team:
			qs = qs.filter(team=team)
		table = BuerotagTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Bürotage"
		context['filter'] = BuerotagFilter(self.request.GET, queryset=Buerotag.objects.filter(archiv=False, team__in=get_buero_list(self.request)))
		return context

class BuerotageChangeView(MyDetailView):
	form_class = BuerotagChgForm
	auth_name = 'Einsatztage.change_buero'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Bürotag ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Buerotag.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		if form.is_valid():
			post = request.POST.dict()
			buero = Buerotag.objects.get(pk=kwargs['pk'])
			if post['koordinator'] != "":
				buero.mitarbeiter=Koordinator.objects.get(pk=int(post['koordinator']))
			buero.updated_by = request.user
			buero.save()
			messages.success(request, 'Bürotag "<a href="'+request.path+'">'+str(buero.datum)+' '+str(buero.team)+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Einsatztage/buero/')
		else:
			messages.error(request, form.errors)

		return render(request, self.template_name, context)		