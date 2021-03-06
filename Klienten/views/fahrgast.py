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
from Einsatztage.views import FahrplanAsPDF
from Klienten.filters import FahrgaesteFilter
from Klienten.forms import FahrgastAddForm, FahrgastChgForm
from Klienten.models import Klienten, Orte, Strassen
from Klienten.tables import FahrgaesteTable
from Klienten.utils import GeoLocation

register = template.Library()


class FahrgastView(MyListView):
    permission_required = 'Klienten.view_klienten'
    model = Klienten

    def get_fg_queryset(self):
        if settings.ALLOW_OUTSIDE_CLIENTS:
            return Klienten.objects.order_by(
                'name', 'ort').filter(
                typ='F', bus__in=get_bus_list(self.request)) | Klienten.objects.order_by(
                'name', 'ort').filter(
                typ='F', bus__isnull=True)
        else:
            return Klienten.objects.order_by('name', 'ort').filter(typ='F', bus__in=get_bus_list(self.request))

    def get_queryset(self):
        name = self.request.GET.get('name')
        ort = self.request.GET.get('ort')
        bus = self.request.GET.get('bus')
        sort = self.request.GET.get('sort')
        qs = self.get_fg_queryset()
        if name:
            qs = qs.filter(name__istartswith=name)
        if ort:
            qs = qs.filter(ort=ort)
        if bus:
            if bus == 'null':
                qs = qs.filter(bus=None)
            else:            
                qs = qs.filter(bus=bus)
        if sort:
            qs = qs.order_by(sort)
        return FahrgaesteTable(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Fahrgäste"
        if self.request.user.has_perm('Klienten.add_klienten'):
            context['add'] = "Fahrgast"
        context['filter'] = FahrgaesteFilter(self.request.GET.copy(), queryset=self.get_fg_queryset())
        return context


class FahrgastAddView(MyCreateView):
    form_class = FahrgastAddForm
    permission_required = 'Klienten.add_klienten'
    success_url = '/Klienten/fahrgaeste/'
    model = Klienten

    def get_context_data(self, **kwargs):
        context = {}
        context['sidebar_liste'] = get_sidebar(self.request.user)
        context['title'] = "Fahrgast hinzufügen"
        context['submit_button'] = "Sichern"
        context['back_button'] = ["Abbrechen", self.success_url+url_args(self.request)]
        context['popup'] = self.request.GET.get('_popup', None)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.initial['typ'] = 'F'
        form = self.form_class(initial=self.initial)
        # nur managed orte anzeigen
        if settings.ALLOW_OUTSIDE_CLIENTS:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(
                bus__in=get_bus_list(request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
        else:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
        context['form'] = form
        return render(request, self.template_name, context)

    def form_invalid(self, form):
        context = self.get_context_data()
        # nur managed orte anzeigen
        if settings.ALLOW_OUTSIDE_CLIENTS:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(
                bus__in=get_bus_list(self.request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
        else:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(self.request))
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.ort.bus != None:
            instance.bus = instance.ort.bus
        if instance.latitude == 0 or set(['ort', 'strasse', 'hausnr']).intersection(set(form.changed_data)):
            GeoLocation().getLocation(instance)
        instance.created_by = self.request.user
        instance.save()
        self.success_message = 'Fahrgast "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+instance.name+'</a>" wurde erfolgreich hinzugefügt.'
        self.success_url += url_args(self.request)
        return super(FahrgastAddView, self).form_valid(form)


class FahrgastChangeView(MyUpdateView):
    form_class = FahrgastChgForm
    permission_required = 'Klienten.change_klienten'
    success_url = '/Klienten/fahrgaeste/'
    model = Klienten

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Fahrgast ändern"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form_class(instance=get_object_or_404(Klienten, pk=kwargs['pk']))
        # nur managed orte anzeigen
        if settings.ALLOW_OUTSIDE_CLIENTS:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(
                bus__in=get_bus_list(request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
        else:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(request))
        if form.instance.ort.bus != None:
            form.fields['bus'].widget = forms.HiddenInput()
        context['form'] = form
        return render(request, self.template_name, context)

    def form_invalid(self, form):
        context = self.get_context_data()
        # nur managed orte anzeigen
        if settings.ALLOW_OUTSIDE_CLIENTS:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(
                bus__in=get_bus_list(self.request)) | Orte.objects.order_by('ort').filter(bus__isnull=True)
        else:
            form.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(self.request))
        if form.instance.ort.bus != None:
            form.fields['bus'].widget = forms.HiddenInput()
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.latitude == 0 or set(['ort', 'strasse', 'hausnr']).intersection(set(form.changed_data)):
            GeoLocation().getLocation(instance)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_message = 'Fahrgast "<a href="'+self.success_url+str(instance.id)+'/'+url_args(
            self.request)+'">'+instance.name+'</a>" wurde erfolgreich geändert.'
        self.success_url += url_args(self.request)
        return super(FahrgastChangeView, self).form_valid(form)


class FahrgastDeleteView(MyDeleteView):
    permission_required = 'Klienten.delete_klienten'
    success_url = '/Klienten/fahrgaeste/'
    model = Klienten

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Fahrgast löschen"
        return context


class DSGVOView(MyDetailView):
    permission_required = 'Klienten.view_klienten'
    success_url = '/Klienten/fahrgaeste/'
    template_name = 'Klienten/dsgvo.html'
    context_object_name = 'klient'

    def get_queryset(self):
        return Klienten.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_liste'] = get_sidebar(self.request.user)
        context['title'] = "DSGVO anzeigen"
        context['back_button'] = ["Zurück", self.success_url+url_args(self.request)]
        return context


class DSGVOasPDFView(MyView):
    permission_required = 'Klienten.view_klienten'
    success_url = '/Klienten/fahrgaeste/'

    def get(self, request, id):
        klient = get_object_or_404(Klienten, pk=id)
        context = {'klient': klient}
        filename = "DSGVO_{}_{}.pdf".format(klient.nachname, klient.vorname)
        pdf = FahrplanAsPDF().pdf_render_to_response('Klienten/dsgvo.rml', context, filename)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            content = "inline; filename='%s'" % (filename)
            filepath = settings.DSGVO_PATH + filename
            try:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                f.close()
                response = FileResponse(open(filepath, 'rb'), content_type="application/pdf")
                response["Content-Disposition"] = "filename={}".format(filename)
                return response
            except:
                messages.error(request, 'Dokument <b>'+filename+'</b> ist noch geöffnet.')
            return HttpResponseRedirect(self.success_url+url_args(request))
        return HttpResponse("Kein Dokument vorhanden")
