from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader

from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView)

from ..forms import MyGroupChangeForm
from ..models import MyGroup
from ..tables import GroupTable


class GroupView(MyListView):
    permission_required = 'auth.view_group'
    model = MyGroup

    def get_queryset(self):
        qs = self.model.objects.order_by('name')
        table = GroupTable(qs)
        table.paginate(page=self.request.GET.get("page", 1), per_page=20)
        return table


class GroupAddView(MyCreateView):
    permission_required = 'auth.add_group'
    form_class = MyGroupChangeForm
    success_url = '/Accounts/gruppen/'
    model = MyGroup

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()
        self.success_url += url_args(self.request)
        self.success_message = self.model._meta.verbose_name.title(
        )+' "<a href="'+self.success_url+str(instance.id)+'">'+instance.name+'</a>" wurde erfolgreich angelegt.'
        return super(GroupAddView, self).form_valid(form)


class GroupChangeView(MyUpdateView):
    permission_required = 'auth.change_group'
    form_class = MyGroupChangeForm
    success_url = '/Accounts/gruppen/'
    model = MyGroup

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        instance = get_object_or_404(self.model, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save()
        messages.success(self.request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url +
                         str(instance.id) + '">' + instance.name + '</a>" wurde erfolgreich geändert.')
        return super(GroupChangeView, self).form_valid(form)


class GroupDeleteView(MyDeleteView):
    permission_required = 'auth.delete_group'
    success_url = '/Accounts/gruppen/'
    model = MyGroup
