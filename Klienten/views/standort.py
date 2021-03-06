import subprocess

from django import forms, template
from django.conf import settings
from django.contrib import messages
from django.http import (FileResponse, Http404, HttpResponse,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from jet.filters import RelatedFieldAjaxListFilter

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Klienten.forms import StandortAddForm, StandortChgForm
from Klienten.models import Klienten, Orte, Strassen
from Klienten.tables import StandorteTable
from Klienten.utils import GeoLocation

register = template.Library()


class StandortView(MyListView):
    permission_required = 'Einsatzmittel.change_bus'
    model = Klienten

    def get_queryset(self):
        qs = Klienten.objects.order_by('name', 'ort').filter(typ='S')
        return StandorteTable(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Bus Standorte"
        if self.request.user.has_perm('Klienten.add_klienten'):
            context['add'] = "Standort"
        return context


class StandortAddView(MyCreateView):
    form_class = StandortAddForm
    permission_required = 'Einsatzmittel.change_bus'
    success_url = '/Klienten/standorte/'
    model = Klienten

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Bus Standort hinzufügen"
        context['popup'] = self.request.GET.get('_popup', None)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.initial['typ'] = 'S'
        form = self.form_class(initial=self.initial)
        form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
        context['form'] = form
        return render(request, self.template_name, context)

    def form_invalid(self, form):
        context = self.get_context_data()
        form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(self.request))
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.latitude == 0 or set(['ort', 'strasse', 'hausnr']).intersection(set(form.changed_data)):
            GeoLocation().getLocation(instance)
        instance.created_by = self.request.user
        instance.save()
        self.success_message = 'Bus Standort "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+instance.name+'</a>" wurde erfolgreich hinzugefügt.'
        self.success_url += url_args(self.request)
        return super(StandortAddView, self).form_valid(form)


class StandortChangeView(MyUpdateView):
    form_class = StandortChgForm
    permission_required = 'Einsatzmittel.change_bus'
    success_url = '/Klienten/standorte/'
    model = Klienten

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Bus Standort ändern"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form_class(instance=get_object_or_404(Klienten, pk=kwargs['pk']))
        form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
        context['form'] = form
        return render(request, self.template_name, context)

    def form_invalid(self, form):
        context = self.get_context_data()
        form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(self.request))
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.latitude == 0 or set(['ort', 'strasse', 'hausnr']).intersection(set(form.changed_data)):
            GeoLocation().getLocation(instance)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_message = 'Bus Standort "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+instance.name+'</a>" wurde erfolgreich geändert.'
        self.success_url += url_args(self.request)
        return super(StandortChangeView, self).form_valid(form)


class StandortDeleteView(MyDeleteView):
    permission_required = 'Einsatzmittel.delete_bus'
    success_url = '/Klienten/standorte/'
    model = Klienten

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Bus Standort löschen"
        return context
