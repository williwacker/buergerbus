import re
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
										PermissionRequiredMixin)
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
	CreateView, DeleteView, DetailView, ListView, UpdateView, View)
from django.views.generic.detail import BaseDetailView

from Basis.multiform import MultiFormsView
from Basis.utils import get_relation_dict, get_sidebar, url_args, get_index_bar, run_command


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

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = self.model._meta.verbose_name_plural
		context['sidebar_liste'] = get_sidebar(self.request.user)
		add_perm = re.sub("view","add",self.permission_required)
		if self.request.user.has_perm(add_perm): context['add'] = self.model._meta.verbose_name_raw	
		return context	

	def dispatch(self, request, *args, **kwargs):
		request.session.pop('suchname','')
		request.session.pop('suchort','')
		request.session.pop('clientsearch_choice','')
		return super(MyListView, self).dispatch(request, *args, **kwargs)

class MyDetailView(SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/detail.html'

class MyCreateView(SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/detail.html'	

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name+" hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context	
	
	def form_invalid(self, form):
		context = self.get_context_data()
		context['form'] = form
		messages.error(self.request, form.errors)			
		return render(self.request, self.template_name, context)
	
class MyMultiFormsView(LoginRequiredMixin, PermissionRequiredMixin, MultiFormsView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/multiforms.html'

class MyView(LoginRequiredMixin, PermissionRequiredMixin, View):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/simple_table.html'

class MyUpdateView(SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/detail.html'

	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name_raw+" ändern"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		del_perm = re.sub("change","delete",self.permission_required)
		if self.request.user.has_perm(del_perm): context['delete_button'] = "Löschen"
		context['url_args'] = url_args(self.request)
		return context	
		
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		instance=get_object_or_404(self.model, pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		context['form'] = form
		return render(request, self.template_name, context)	
	
	def form_invalid(self, form):
		context = self.get_context_data()
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

	def post(self, request, *args, **kwargs):
		instance = get_object_or_404(self.model, pk=kwargs['pk'])
		messages.success(request, self.model._meta.verbose_name_raw+' "'+str(instance)+'" wurde gelöscht.')
		return self.delete(request, *args, **kwargs)

class BasisView(LoginRequiredMixin, ListView):
	login_url = settings.LOGIN_URL
	template_name = 'Basis/index.html'

	def get_queryset(self):
		return None

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
#		context['git_revision'] = 'V{}-{}'.format(run_command('git describe --abbrev=0'),run_command('git rev-list --count HEAD'))
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['indexbar_liste'] = get_index_bar(self.request.user)
		return context

class MyBaseDetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
	login_url = settings.LOGIN_URL
