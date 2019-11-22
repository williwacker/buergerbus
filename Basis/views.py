from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from Basis.multiform import MultiFormsView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .utils import get_sidebar, get_relation_dict

def my_custom_bad_request_view(request, exception):  #400
    return render(request,'Basis/400.html')

def my_custom_permission_denied_view(request, exception):  #403
    return render(request,'Basis/403.html')

def my_custom_error_view(request):  #500
    return render(request,'Basis/500.html')

def my_custom_page_not_found_view(request, exception):  #404
    return render(request,'Basis/404.html')

class MyListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/simple_table.html'
	context_object_name = 'table'

	def dispatch(self, request, *args, **kwargs):
		request.session.pop('suchname','')
		request.session.pop('suchort','')
		request.session.pop('clientsearch_choice','')
		return super(MyListView, self).dispatch(request, *args, **kwargs)

class MyDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	initial = {'key': 'value'}
	template_name = 'Basis/detail.html'

class MyMultiFormsView(LoginRequiredMixin, PermissionRequiredMixin, MultiFormsView):
	login_url = settings.LOGIN_URL
	initial = {'key': 'value'}
	template_name = 'Basis/multiforms.html'

class MyView(LoginRequiredMixin, PermissionRequiredMixin, View):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/simple_table.html'

class MyUpdateView(SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/detail.html'

	def form_invalid(self, form):
		context = self.get_context_data(self.request)
		form = self.form_class(self.request.POST)
		context['form'] = form
		messages.error(self.request, form.errors)			
		return render(self.request, self.template_name, context)

class MyDeleteView(SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/confirm_delete.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['related_objects'] = get_relation_dict(self.model, kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name_raw+" löschen"
		context['submit_button'] = "Ja, ich bin sicher"
		context['back_button'] = "Nein, bitte abbrechen"
		return context		

class BasisView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/index.html'

	def get_queryset(self):
		return None

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		return context

		