import subprocess

from django import forms, template
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from fuzzywuzzy import fuzz, process
from jet.filters import RelatedFieldAjaxListFilter

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Klienten.filters import OrteFilter
from Klienten.forms import OrtAddForm, OrtChgForm
from Klienten.models import Orte
from Klienten.tables import OrteTable

register = template.Library()


class OrtView(MyListView):
    permission_required = 'Klienten.view_orte'
    model = Orte

    def get_queryset(self):
        ort = self.request.GET.get('ort')
        plz = self.request.GET.get('plz')
        bus = self.request.GET.get('bus')
        qs = Orte.objects.order_by('ort')
        if ort:
            qs = qs.filter(ort=ort)
        if plz:
            qs = qs.filter(plz=plz)
        if bus:
            if bus == 'null':
                qs = qs.filter(bus=None)
            else:        
                qs = qs.filter(bus=bus)
        return OrteTable(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = OrteFilter(self.request.GET.copy(), queryset=Orte.objects.order_by('ort'))
        return context


class OrtAddView(MyCreateView):
    form_class = OrtAddForm
    permission_required = 'Klienten.add_orte'
    success_url = '/Klienten/orte/'
    model = Orte

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popup'] = self.request.GET.get('_popup', None)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form_class(initial=self.initial)
        # bus darf nur vom superuser hinzugefügt werden
        if not request.user.is_superuser:
            form.fields['bus'].widget = forms.HiddenInput()
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()
        self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(
            instance.id)+'/'+url_args(self.request)+'">'+str(instance)+'</a>" wurde erfolgreich hinzugefügt.'
        self.success_url += url_args(self.request)
        return super(OrtAddView, self).form_valid(form)


class OrtChangeView(MyUpdateView):
    form_class = OrtChgForm
    permission_required = 'Klienten.change_orte'
    success_url = '/Klienten/orte/'
    model = Orte

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        instance = get_object_or_404(Orte, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        # bus darf nur vom superuser geändert werden
        if not request.user.is_superuser:
            form.fields['bus'].widget = forms.HiddenInput()
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_message = 'Ort "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+instance.ort+'</a>" wurde erfolgreich geändert.'
        self.success_url += url_args(self.request)
        return super(OrtChangeView, self).form_valid(form)


class OrtDeleteView(MyDeleteView):
    permission_required = 'Klienten.delete_orte'
    success_url = '/Klienten/orte/'
    model = Orte
    pass
