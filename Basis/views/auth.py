from django.contrib import messages
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.contrib.auth import login as auth_login
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.generic import TemplateView

from Basis.models import MyUser, MyGroup
from Basis.forms import MyGroupChangeForm, MyUserCreationForm, MyUserChangeForm
from Basis.tables import GroupTable, UserTable
from Basis.utils import get_sidebar, url_args
from Basis.views import MyDeleteView, MyCreateView, MyDetailView, MyListView, MyUpdateView, MyView

# User Views
class UserView(MyListView):
	permission_required = 'auth.view_user'
	model = MyUser

	def get_queryset(self):
		qs = self.model.objects.order_by('username')
		if not self.request.user.is_superuser:
			qs = qs.exclude(is_superuser=True)
		table = UserTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table


class UserAddView(MyCreateView):
	permission_required = 'auth.add_user'
	form_class = MyUserCreationForm
	success_url = '/Basis/benutzer/'
	model = MyUser

	def form_valid(self, form):
		user = form.save(commit=False)
		password = self.model.objects.make_random_password()
		user.set_password(password)
		user.created_by = self.request.user
		current_site = get_current_site(self.request)
		site_name = current_site.name
		domain = current_site.domain
		context = {
			'username': user.username,
			'password': user._password,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'protocol': 'https' if self.request.is_secure() else 'http',
			'domain'  : domain
		}
		email = EmailMessage(
			'[Bürgerbus] Ihr Benutzername',
			loader.render_to_string('registration/password_new_email.html', context),
			settings.DEFAULT_FROM_EMAIL,
			(user.email,),
		)
		email.send(fail_silently=False)
		user.save()		
		self.success_url += url_args(self.request)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(user.id)+'">'+user.username+'</a>" wurde erfolgreich angelegt.'
		return super(UserAddView, self).form_valid(form)


class UserChangeView(MyUpdateView):
	permission_required = 'auth.change_user'
	form_class = MyUserChangeForm
	model=MyUser
	success_url = '/Basis/benutzer/'

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		instance=get_object_or_404(self.model, pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		if not self.request.user.is_superuser:
			# only the owned groups and user_permissions can be assigned
			form.fields['groups'].queryset = \
				form.fields['groups'].queryset.filter(id__in=[i.id for i in self.request.user.groups.all()])
			form.fields['user_permissions'].queryset = \
				form.fields['user_permissions'].queryset.filter(id__in=[i.id for i in self.request.user.user_permissions.all()])
			form.fields['is_superuser'].widget = forms.HiddenInput()
			form.fields['is_staff'].widget = forms.HiddenInput()
			form.fields['password'].widget = forms.HiddenInput()
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save()
		messages.success(self.request, 'Benutzer "<a href="'+self.success_url+str(instance.id)+'">'+instance.username+'</a>" wurde erfolgreich geändert.')
		return super(UserChangeView, self).form_valid(form) 


class UserDeleteView(MyDeleteView):
	permission_required = 'auth.delete_user'
	success_url = '/Basis/benutzer/'
	model = MyUser

# Gruppen

class GroupView(MyListView):
	permission_required = 'auth.view_group'
	model=MyGroup
	
	def get_queryset(self):
		qs = self.model.objects.order_by('name')
		table = GroupTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table


class GroupAddView(MyCreateView):
	permission_required = 'auth.change_group'
	form_class = MyGroupChangeForm
	success_url = '/Basis/gruppen/'
	model=MyGroup

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_url += url_args(self.request)
		self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich angelegt.'
		return super(GroupAddView, self).form_valid(form)


class GroupChangeView(MyUpdateView):
	permission_required = 'auth.change_group'
	form_class = MyGroupChangeForm
	success_url = '/Basis/gruppen/'
	model=MyGroup
	
	def form_valid(self, form):
		instance = form.save()
		storage = messages.get_messages(self.request)
		storage.used = True			
		messages.success(self.request, self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich geändert.')
		return super(GroupChangeView, self).form_valid(form) 

class GroupDeleteView(MyDeleteView):
	permission_required = 'auth.delete_group'
	success_url = '/Basis/gruppen/'
	model = MyGroup


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
		context['sidebar_liste'] = get_sidebar(self.request.user)
		return context
