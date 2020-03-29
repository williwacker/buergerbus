import logging

from django import forms, template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.http import (FileResponse, Http404, HttpResponse,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from trml2pdf import trml2pdf

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Klienten.models import Klienten
from Team.models import Fahrer
from Tour.models import Tour

from ..filters import FahrtagFilter
from ..forms import FahrtagAddForm, FahrtagChgForm
from ..models import Fahrtag
from ..tables import FahrerTable, FahrtagTable, TourTable
from ..utils import FahrtageSchreiben

logger = logging.getLogger(__name__)

register = template.Library()


class FahrtageListView(MyListView):
    permission_required = 'Einsatztage.view_fahrtag'
    model = Fahrtag

    def get_queryset(self):
        if self.request.user.has_perm('Einsatztage.change_fahrtag'):
            FahrtageSchreiben()
        team = self.request.GET.get('team')
        sort = self.request.GET.get('sort')
        qs = Fahrtag.objects.order_by('datum', 'team').filter(archiv=False, team__in=get_bus_list(self.request))
        if team:
            qs = qs.filter(team=team)
        if sort:
            qs = qs.order_by(sort)
        table = FahrtagTable(qs)
        table.paginate(page=self.request.GET.get("page", 1), per_page=20)
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = FahrtagFilter(self.request.GET.copy(), queryset=Fahrtag.objects.filter(
            archiv=False, team__in=get_bus_list(self.request)))
        return context


class FahrtageAddView(MyCreateView):
    form_class = FahrtagAddForm
    permission_required = 'Einsatztage.add_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()
        self.success_url += url_args(self.request)
        self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(
            instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich hinzugefügt.'
        return super(FahrtageAddView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form_class()
        form.fields['team'].queryset = Bus.objects.filter(id__in=get_bus_list(self.request))
        context['form'] = form
        return render(request, self.template_name, context)


class FahrtageChangeView(MyUpdateView):
    form_class = FahrtagChgForm
    permission_required = 'Einsatztage.change_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        instance = get_object_or_404(self.model, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        form.fields['fahrer_vormittag'].queryset = Fahrer.objects.filter(aktiv=True, team=instance.team)
        form.fields['fahrer_nachmittag'].queryset = Fahrer.objects.filter(aktiv=True, team=instance.team)
        context['form'] = form
        return render(request, self.template_name, context)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        logger.info("Initial Datum {}, Returned Datum {}, Changed Fields {}".format(
            form.initial['datum'], instance.datum, form.changed_data))
        if instance.fahrer_vormittag:
            # auf doppelte Buchung am gleichen Tag prüfen
            fahrtag = Fahrtag.objects.filter(
                fahrer_vormittag__benutzer=instance.fahrer_vormittag.benutzer, datum=instance.datum).exclude(
                team=instance.team).first()
            if fahrtag:
                messages.error(self.request, str(fahrtag.fahrer_vormittag) + ' ist am ' + str(instance.datum) +
                               ' Vormittag bereits für ' + str(fahrtag.team) + ' gebucht.')
                return HttpResponseRedirect(self.success_url+url_args(self.request))
        if instance.fahrer_nachmittag:
            # auf doppelte Buchung am gleichen Tag prüfen
            fahrtag = Fahrtag.objects.filter(
                fahrer_nachmittag__benutzer=instance.fahrer_nachmittag.benutzer, datum=instance.datum).exclude(
                team=instance.team).first()
            if fahrtag:
                messages.error(
                    self.request, str(fahrtag.fahrer_nachmittag) + ' ist am ' + str(instance.datum) +
                    ' Nachmittag bereits für ' + str(fahrtag.team) + ' gebucht.')
                return HttpResponseRedirect(self.success_url+url_args(self.request))
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_url += url_args(self.request)
        self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(
            instance.id)+'">'+str(instance.datum)+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
        return super(FahrtageChangeView, self).form_valid(form)


class FahrtageBookvView(MyView):
    permission_required = 'Einsatztage.change_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag

    def get(self, request, pk):
        instance = get_object_or_404(self.model, pk=pk)
        fahrer = Fahrer.objects.filter(benutzer=request.user, aktiv=True, team=instance.team).first()
        if not fahrer:  # nicht als aktiver Fahrer eingetragen
            messages.error(request, self.model._meta.verbose_name.title() + ' am ' + str(instance.datum) + ' ' +
                           str(instance.team) + ' kann nicht von Ihnen gebucht werden. Sie sind kein aktiver Fahrer.')
        else:
            fahrtag = Fahrtag.objects.filter(
                fahrer_vormittag__benutzer=fahrer.benutzer, datum=instance.datum).exclude(
                team=instance.team).first()
            if instance.fahrer_vormittag != None:  # Vormittag bereits gebucht
                messages.error(request, self.model._meta.verbose_name.title(
                )+' am '+str(instance.datum)+' '+str(instance.team)+' ist bereits gebucht.')
            elif fahrtag:  # auf doppelte Buchung am gleichen Tag prüfen
                messages.error(
                    self.request, 'Sie sind am ' + str(instance.datum) + ' Vormittag bereits für ' + str(fahrtag.team) +
                    ' gebucht.')
            else:
                instance.fahrer_vormittag = fahrer
                instance.save()
                messages.success(
                    request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url + str(instance.id) +
                    '">' + str(instance.datum) + ' ' + str(instance.team) + '</a>" wurde erfolgreich geändert.')
        return HttpResponseRedirect(self.success_url+url_args(request))


class FahrtageBooknView(MyView):
    permission_required = 'Einsatztage.change_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag

    def get(self, request, pk):
        instance = get_object_or_404(Fahrtag, pk=pk)
        fahrer = Fahrer.objects.filter(benutzer=request.user, aktiv=True, team=instance.team).first()
        if not fahrer:  # nicht als aktiver Fahrer eingetragen
            messages.error(request, self.model._meta.verbose_name.title() + ' am ' + str(instance.datum) + ' ' +
                           str(instance.team) + ' kann nicht von Ihnen gebucht werden. Sie sind kein aktiver Fahrer.')
        else:
            fahrtag = Fahrtag.objects.filter(
                fahrer_nachmittag__benutzer=fahrer.benutzer, datum=instance.datum).exclude(
                team=instance.team).first()
            if instance.fahrer_nachmittag != None:  # Nachmittag bereits gebucht
                messages.error(request, self.model._meta.verbose_name.title(
                )+' am '+str(instance.datum)+' '+str(instance.team)+' ist bereits gebucht.')
            elif fahrtag:  # auf doppelte Buchung am gleichen Tag prüfen
                messages.error(
                    self.request, 'Sie sind am ' + str(instance.datum) + ' Nachmittag bereits für ' + str(fahrtag.team) +
                    ' gebucht.')
            else:
                instance.fahrer_nachmittag = fahrer
                instance.save()
                messages.success(
                    request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url + str(instance.id) +
                    '">' + str(instance.datum) + ' ' + str(instance.team) + '</a>" wurde erfolgreich geändert.')
        return HttpResponseRedirect(self.success_url+url_args(request))


class FahrtageCancelvView(MyUpdateView):
    permission_required = 'Einsatztage.change_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag

    def get(self, request, pk):
        instance = get_object_or_404(Fahrtag, pk=pk)
        fahrer = Fahrer.objects.filter(benutzer=request.user, team=instance.team).first()
        if instance.fahrer_vormittag != fahrer:
            messages.error(request, self.model._meta.verbose_name.title(
            )+' am '+str(instance.datum)+' '+str(instance.team)+' ist nicht auf Sie gebucht.')
        else:
            instance.fahrer_vormittag = None
            instance.save()
            messages.success(request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url +
                             str(instance.id) + '">' + str(instance.datum) + ' ' + str(instance.team) +
                             '</a>" wurde erfolgreich geändert.')
        return HttpResponseRedirect(self.success_url+url_args(request))


class FahrtageCancelnView(MyUpdateView):
    permission_required = 'Einsatztage.change_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag

    def get(self, request, pk):
        instance = get_object_or_404(Fahrtag, pk=pk)
        fahrer = Fahrer.objects.filter(benutzer=request.user, team=instance.team).first()
        if instance.fahrer_nachmittag != fahrer:
            messages.error(request, self.model._meta.verbose_name.title(
            )+' am '+str(instance.datum)+' '+str(instance.team)+' ist nicht auf Sie gebucht.')
        else:
            instance.fahrer_nachmittag = None
            instance.save()
            messages.success(request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url +
                             str(instance.id) + '">' + str(instance.datum) + ' ' + str(instance.team) +
                             '</a>" wurde erfolgreich geändert.')
        return HttpResponseRedirect(self.success_url+url_args(request))


class FahrtageDeleteView(MyDeleteView):
    permission_required = 'Einsatztage.delete_fahrtag'
    success_url = '/Einsatztage/fahrer/'
    model = Fahrtag
    pass
