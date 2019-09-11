from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
#from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .utils import has_perm, get_sidebar
from .tables import UserTable, GroupTable
from .views import MyListView, MyDetailView, MyUpdateView, MyView
from .forms import MyUserChangeForm, MyGroupChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView

class UserView(MyListView):
	auth_name = 'auth.view_user'
	
	def get_queryset(self):
		qs = User.objects.order_by('username')
		table = UserTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['add'] = "Benutzer"
		context['title'] = "Benutzer"
		return context		

class UserAddView(MyDetailView):
	auth_name = 'auth.change_user'
	form_class = UserCreationForm

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Benutzer hinzufügen"
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
			form.save()	
#			messages.success(request, 'Benutzer "<a href="'+request.path+'">'+user.username+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect('/Basis/benutzer/')
		else:
			messages.error(request, form.errors)
		
		return render(request, self.template_name, context)

class UserChangeView(MyUpdateView):
	auth_name = 'auth.change_user'
	form_class = MyUserChangeForm
	model=User
	success_url = '/Basis/benutzer/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Benutzer ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context
	
class UserDeleteView(MyView):
	auth_name = 'auth.delete_user'
	def get(self, request, *args, **kwargs):
		u = User.objects.get(pk=kwargs['pk'])
		u.delete()
		messages.success(request, 'Benutzer '+u.username+' wurde gelöscht.')
		return HttpResponseRedirect('/Basis/benutzer/')

# Gruppen

class GroupView(MyListView):
	auth_name = 'auth.view_group'
	
	def get_queryset(self):
		qs = Group.objects.order_by('name')
		table = GroupTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=20)
		return table

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['add'] = "Gruppe"
		context['title'] = "Gruppen"
		return context

class GroupAddView(MyDetailView):
	auth_name = 'auth.change_group'
	form_class = MyGroupChangeForm

	def get_context_data(self, request):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Gruppe hinzufügen"
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
			form.save()	
#			messages.success(request, 'Gruppe "<a href="'+request.path+'">'+user.username+'</a>" wurde erfolgreich hinzugefügt.')
			context['messages'] = messages
			return HttpResponseRedirect('/Basis/gruppen/')
		else:
			messages.error(request, form.errors)
		
		return render(request, self.template_name, context)

class GroupChangeView(MyUpdateView):
	auth_name = 'auth.change_group'
	form_class = MyGroupChangeForm
	model=Group
	success_url = '/Basis/gruppen/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Benutzer ändern"
		context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = "Abbrechen"
		return context

class GroupDeleteView(MyView):
	auth_name = 'auth.delete_group'
	def get(self, request, *args, **kwargs):
		g = Group.objects.get(pk=kwargs['pk'])
		g.delete()
		messages.success(request, 'Gruppe '+g.name+' wurde gelöscht.')
		return HttpResponseRedirect('/Basis/gruppen/')