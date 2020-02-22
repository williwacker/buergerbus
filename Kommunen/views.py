from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyDeleteView, MyCreateView, MyListView, MyUpdateView,
						 MyView)
from Kommunen.forms import KommuneAddForm, KommuneChgForm
from Kommunen.models import Kommunen
from Kommunen.tables import KommunenTable

register = template.Library()

class KommunenView(MyListView):
	permission_required = 'Kommunen.view_kommunen'
	model = Kommunen

	def get_queryset(self):
		qs = Kommunen.objects.order_by('name')
		return KommunenTable(qs)

#	def get_context_data(self, **kwargs):
#		context = super().get_context_data(**kwargs)
#		return context

class KommuneAddView(MyCreateView):
	form_class = KommuneAddForm
	permission_required = 'Kommunen.add_kommunen'
	success_url = '/Kommunen/kommunen/'
	model = Kommunen

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+str(instance)+'</a>" wurde erfolgreich hinzugefügt.'
		self.success_url += url_args(self.request)
		return super(KommuneAddView, self).form_valid(form)

	def form_invalid(self, form):
		context = self.get_context_data()
		context['form'] = form
		messages.error(self.request, form.errors)			
		return render(self.request, self.template_name, context)		

class KommuneChangeView(MyUpdateView):
	form_class = KommuneChgForm
	permission_required = 'Kommunen.change_kommunen'
	success_url = '/Kommunen/kommunen/'
	model = Kommunen

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance)+'</a>" wurde erfolgreich geändert.'
		return super(KommuneChangeView, self).form_valid(form) 

class KommuneDeleteView(MyDeleteView):
	permission_required = 'Kommunen.delete_kommunen'
	success_url = '/Kommunen/kommunen/'
	model = Kommunen
	
	def post(self, request, *args, **kwargs):
		instance = get_object_or_404(self.model, pk=kwargs['pk'])
		messages.success(request, self.model._meta.verbose_name_raw+' "'+str(instance)+'" wurde gelöscht.')
		return self.delete(request, *args, **kwargs)