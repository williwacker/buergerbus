import subprocess

from django import forms, template
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from jet.filters import RelatedFieldAjaxListFilter

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Klienten.filters import StrassenFilter
from Klienten.forms import StrassenAddForm, StrassenChgForm
from Klienten.models import Orte, Strassen
from Klienten.tables import StrassenTable

register = template.Library()


class StrassenView(MyListView):
    permission_required = 'Klienten.view_strassen'
    model = Strassen

    def get_queryset(self):
        ort = self.request.GET.get('ort')
        strasse = self.request.GET.get('strasse')
        qs = Strassen.objects.order_by('ort', 'strasse')
        if ort:
            qs = qs.filter(ort=ort)
        if strasse:
            qs = qs.filter(strasse=strasse)
        table = StrassenTable(qs)
        table.paginate(page=self.request.GET.get("page", 1), per_page=20)
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = StrassenFilter(self.request.GET.copy())
        return context


class StrassenAddView(MyCreateView):
    form_class = StrassenAddForm
    permission_required = 'Klienten.add_strassen'
    success_url = '/Klienten/strassen/'
    model = Strassen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popup'] = self.request.GET.get('_popup', None)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        ort = request.GET.get('ort')
        self.initial['ort'] = Orte.objects.get(id=str(ort)) if ort else None
        form = self.form_class(initial=self.initial)
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()
        self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+str(instance)+' in '+str(instance.ort)+'</a>" wurde erfolgreich hinzugefügt.'
        self.success_url += url_args(self.request)
        return super(StrassenAddView, self).form_valid(form)


class StrassenChangeView(MyUpdateView):
    form_class = StrassenChgForm
    permission_required = 'Klienten.change_strassen'
    success_url = '/Klienten/strassen/'
    model = Strassen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Strasse ändern"
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_message = 'Strasse "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+instance.strasse+'</a>" wurde erfolgreich geändert.'
        self.success_url += url_args(self.request)
        return super(StrassenChangeView, self).form_valid(form)


class StrassenDeleteView(MyDeleteView):
    permission_required = 'Klienten.delete_strassen'
    success_url = '/Klienten/strassen/'
    model = Strassen
    pass
