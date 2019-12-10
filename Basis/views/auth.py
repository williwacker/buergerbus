from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import TemplateView
from Basis.utils import get_sidebar, url_args
from Basis.tables import UserTable, GroupTable
from Basis.views import MyListView, MyDetailView, MyUpdateView, MyView, MyDeleteView
from Basis.forms import MyUserChangeForm, MyGroupChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView

class UserView(MyListView):
	permission_required = 'auth.view_user'
	
	def get_queryset(self):
		qs = User.objects.order_by('username')
		table = UserTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		if self.request.user.has_perm('auth.change_user'):
			context['add'] = "Benutzer"
		context['title'] = "Benutzer"
		context['url_args'] = url_args(self.request)
		return context

class UserAddView(MyDetailView):
	permission_required = 'auth.change_user'
	form_class = UserCreationForm
	success_url = '/Basis/benutzer/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Benutzer hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]	
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
			instance = form.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Benutzer "<a href="'+self.success_url+str(instance.id)+'">'+instance.username+'</a>" wurde erfolgreich angelegt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)
		
		return render(request, self.template_name, context)

class UserChangeView(MyUpdateView):
	permission_required = 'auth.change_user'
	form_class = MyUserChangeForm
	model=User
	success_url = '/Basis/benutzer/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Benutzer ändern"
		if self.request.user.has_perm('auth.delete_user'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def get_form(self, form_class=None):
		form = super(UserChangeView, self).get_form(self.form_class)
		user = self.request.user
		if not user.is_superuser:
			form.fields['groups'].queryset = form.fields['groups'].queryset.filter(id__in=[i.id for i in user.groups.all()])
			form.fields['user_permissions'].queryset = form.fields['user_permissions'].queryset.filter(id__in=[i.id for i in user.user_permissions.all()])
			form.fields['is_superuser'].widget.attrs['disabled'] = True
		return form
	
	def form_valid(self, form):
		instance = form.save()
		storage = messages.get_messages(self.request)
		storage.used = True			
		messages.success(self.request, 'Benutzer "<a href="'+self.success_url+str(instance.id)+'">'+instance.username+'</a>" wurde erfolgreich geändert.')
		return super(UserChangeView, self).form_valid(form) 

class UserDeleteView(MyDeleteView):
	permission_required = 'auth.delete_user'
	success_url = '/Basis/benutzer/'
	model = User

# Gruppen

class GroupView(MyListView):
	permission_required = 'auth.view_group'
	
	def get_queryset(self):
		qs = Group.objects.order_by('name')
		table = GroupTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		if self.request.user.has_perm('auth.change_group'):
			context['add'] = "Gruppe"
		context['title'] = "Gruppen"
		context['url_args'] = url_args(self.request)
		return context

class GroupAddView(MyDetailView):
	permission_required = 'auth.change_group'
	form_class = MyGroupChangeForm
	success_url = '/Basis/gruppen/'

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Gruppe hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]	
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
			instance = form.save()
			storage = messages.get_messages(request)
			storage.used = True			
			messages.success(request, 'Gruppe "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich hinzugefügt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)	
		return render(request, self.template_name, context)

class GroupChangeView(MyUpdateView):
	permission_required = 'auth.change_group'
	form_class = MyGroupChangeForm
	model=Group
	success_url = '/Basis/gruppen/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Benutzer ändern"
		if self.request.user.has_perm('auth.delete_group'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context
	
	def form_valid(self, form):
		instance = form.save()
		storage = messages.get_messages(self.request)
		storage.used = True			
		messages.success(self.request, 'Gruppe "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich geändert.')
		return super(GroupChangeView, self).form_valid(form) 

class GroupDeleteView(MyDeleteView):
	permission_required = 'auth.delete_group'
	success_url = '/Basis/gruppen/'
	model = Group

class MyPasswordChangeView(PasswordChangeView):

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update({
			'title': self.title,
			**(self.extra_context or {})
		})
		context.update({
			'sidebar_liste':get_sidebar(self.request.user)
		})
		return context

class MyPasswordChangeDoneView(TemplateView):
	template_name = 'registration/password_change_done.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update({
			'sidebar_liste':get_sidebar(self.request.user)
		})
		return context