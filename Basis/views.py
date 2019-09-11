from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .utils import has_perm, get_sidebar

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

class MyUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
	login_url = settings.LOGIN_URL
	auth_name = 'auth.change_user'
	template_name = 'Basis/detail.html'

	def dispatch(self, *args, **kwargs):
		if has_perm(self.request.user,self.auth_name):
			return super(MyUpdateView, self).dispatch(*args, **kwargs)
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