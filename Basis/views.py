from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from Basis.utils import get_sidebar, render_to_pdf
#from admin.models import 

class MyListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL

class MyDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	initial = {'key': 'value'}

class BasisView(MyListView):
	template_name = 'Basis/index.html'
	context_object_name = 'basis_liste'

	def get_queryset(self):
		return None

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		return context

class BenutzerView(MyListView):
	template_name = 'Basis/benutzer.html'
	context_object_name = 'form'
#	model = auth
	
	def get_queryset(self):
		return Orte.objects.order_by('bus','ort')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Orte"
		return context		

class BenutzerAddView(MyDetailView):
#	form_class = BenutzerAddForm
	template_name = "Basis/detail.html"

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
		if form.is_valid():
			post = request.POST.dict()
			ort = Orte(	ort=post['ort'],
						bus=Bus.objects.get(pk=int(post['bus'])),
						updated_by = request.user
					)
			ort.save()
			context['form'] = form		
			messages.success(request, 'Ort "<a href="'+request.path+'">'+ort.ort+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect('/Klienten/orte/')
		
		return render(request, self.template_name, context)

class BenutzerChangeView(MyDetailView):
#	form_class = BenutzerChgForm
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(request.user)
		context['title'] = "Ort ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(instance=Orte.objects.get(pk=kwargs['pk']))
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(request)
		form = self.form_class(request.POST)
		if form.is_valid():
			post = request.POST.dict()
			ort = Orte.objects.get(pk=kwargs['pk'])
			ort.ort=post['ort']
			ort.bus=Bus.objects.get(bus=int(post['bus']))
			ort.updated_by = request.user
			ort.save()
			context['form'] = form
			messages.success(request, 'Ort "<a href="'+request.path+'">'+post['ort']+' Bus '+post['bus']+'</a>" wurde erfolgreich geändert.')
			return HttpResponseRedirect('/Klienten/orte/')

		return render(request, self.template_name, context)		

class BenutzerDeleteView(View):
	def get(self, request, *args, **kwargs):
		k = Benutzer.objects.get(pk=kwargs['pk'])
		k.delete()

		return HttpResponseRedirect('/Klienten/orte/')			