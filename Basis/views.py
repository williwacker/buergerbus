from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .utils import has_perm, get_sidebar, render_to_pdf

def my_custom_bad_request_view(request, exception):  #400
    return render(request,'Basis/400.html')

def my_custom_permission_denied_view(request, exception):  #403
    return render(request,'Basis/403.html')

def my_custom_error_view(request):  #500
    return render(request,'Basis/500.html')

def my_custom_page_not_found_view(request, exception):  #404
    return render(request,'Basis/404.html')

class MyListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/simple_table.html'
	context_object_name = 'table'
	auth_name = 'Einsatztage.view_bus'

	def dispatch(self, *args, **kwargs):
		if has_perm(self.request.user,self.auth_name):
			return super(MyListView, self).dispatch(*args, **kwargs)
		else:
			raise PermissionDenied

class MyDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'
	auth_name = 'Einsatztage.view_bus'

	def dispatch(self, *args, **kwargs):
		if has_perm(self.request.user,self.auth_name):
			return super(MyDetailView, self).dispatch(*args, **kwargs)
		else:
			raise PermissionDenied	

class MyView(LoginRequiredMixin, View):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/simple_table.html'
	auth_name = 'Einsatztage.view_bus'

	def dispatch(self, *args, **kwargs):
		if has_perm(self.request.user,self.auth_name):
			return super(MyView, self).dispatch(*args, **kwargs)
		else:
			raise PermissionDenied	
		
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