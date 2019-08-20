from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from Basis.utils import get_sidebar, render_to_pdf

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