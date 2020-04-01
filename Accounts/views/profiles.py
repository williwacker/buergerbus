from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from Basis.utils import url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView)

from ..forms import MyProfileChangeForm
from ..models import Profile
from ..tables import ProfileTable


class ProfileView(MyListView):
    permission_required = 'auth.view_user'
    model = Profile

    def get_queryset(self):
        qs = self.model.objects.order_by('user')
        table = ProfileTable(qs)
        table.paginate(page=self.request.GET.get("page", 1), per_page=20)
        return table

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        if 'add' in context:
            context.pop('add')
        return context


class ProfileChangeView(MyUpdateView):
    form_class = MyProfileChangeForm
    permission_required = 'auth.change_user'
    success_url = '/Accounts/profile/'
    model = Profile

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        instance = get_object_or_404(self.model, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(ProfileChangeView, self).get_context_data(**kwargs)
        if 'delete_button' in context:
            context.pop('delete_button')
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        messages.success(self.request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url +
                         str(instance.id) + '">' + str(instance.user) + '</a>" wurde erfolgreich geändert.')
        self.success_url += url_args(self.request)
        return super(ProfileChangeView, self).form_valid(form)
