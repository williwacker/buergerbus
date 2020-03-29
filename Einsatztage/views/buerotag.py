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
from Basis.views import MyDetailView, MyListView, MyUpdateView, MyView
from Einsatzmittel.utils import get_buero_list
from Team.models import Fahrer, Koordinator

from ..filters import BuerotagFilter
from ..forms import BuerotagChgForm
from ..models import Buerotag
from ..tables import BuerotagTable
from ..utils import BuerotageSchreiben

logger = logging.getLogger(__name__)

register = template.Library()


class BuerotageListView(MyListView):
    permission_required = 'Einsatztage.view_buerotag'
    model = Buerotag

    def get_queryset(self):
        if self.request.user.has_perm('Einsatztage.change_buerotag'):
            BuerotageSchreiben()
        team = self.request.GET.get('team')
        sort = self.request.GET.get('sort')
        qs = Buerotag.objects.order_by('team', 'datum').filter(archiv=False, team__in=get_buero_list(self.request))
        if team:
            qs = qs.filter(team=team)
        if sort:
            qs = qs.order_by(sort)
        table = BuerotagTable(qs)
        table.paginate(page=self.request.GET.get("page", 1), per_page=20)
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = BuerotagFilter(
            self.request.GET.copy(), queryset=Buerotag.objects.filter(
                archiv=False, team__in=get_buero_list(self.request)))
        if 'add' in context:
            del context['add']
        return context


class BuerotageChangeView(MyUpdateView):
    form_class = BuerotagChgForm
    permission_required = 'Einsatztage.change_buerotag'
    success_url = '/Einsatztage/buero/'
    model = Buerotag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'delete_button' in context:
            del context['delete_button']
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        instance = get_object_or_404(self.model, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        form.fields['koordinator'].queryset = Koordinator.objects.filter(aktiv=True, team=instance.team)
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
        if instance.koordinator:
            # auf doppelte Buchung am gleichen Tag prüfen
            buerotag = Buerotag.objects.filter(
                koordinator__benutzer=instance.koordinator.benutzer, datum=instance.datum).exclude(
                team=instance.team).first()
            if buerotag:
                messages.error(self.request, str(buerotag.koordinator) + ' ist am ' + str(instance.datum) +
                               ' bereits für ' + str(buerotag.team) + ' gebucht.')
                return HttpResponseRedirect(self.success_url+url_args(self.request))
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_url += url_args(self.request)
        self.success_message = self.model._meta.verbose_name.title()+' "<a href="'+self.success_url+str(
            instance.id)+'">'+str(instance.datum)+' in '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
        return super(BuerotageChangeView, self).form_valid(form)


class BuerotageBookView(MyView):
    permission_required = 'Einsatztage.change_buerotag'
    success_url = '/Einsatztage/buero/'
    model = Buerotag

    def get(self, request, pk):
        instance = get_object_or_404(Buerotag, pk=pk)
        koordinator = Koordinator.objects.filter(benutzer=request.user, aktiv=True, team=instance.team).first()
        if not koordinator:
            messages.error(
                request, self.model._meta.verbose_name.title() + ' am ' + str(instance.datum) + ' in ' +
                str(instance.team) + ' kann nicht von Ihnen gebucht werden. Sie sind kein aktiver Koordinator.')
        else:
            buerotag = Buerotag.objects.filter(
                koordinator__benutzer=koordinator.benutzer, datum=instance.datum).exclude(
                team=instance.team).first()
            if instance.koordinator != None:
                messages.error(request, self.model._meta.verbose_name.title(
                )+' am '+str(instance.datum)+' in '+str(instance.team)+' ist bereits gebucht.')
            elif buerotag:
                messages.error(
                    self.request, 'Sie sind am '+str(instance.datum)+' bereits für '+str(buerotag.team)+' gebucht.')
            else:
                instance.koordinator = koordinator
                instance.save()
                messages.success(
                    request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url + str(instance.id) +
                    '">' + str(instance.datum) + ' in ' + str(instance.team) + '</a>" wurde erfolgreich geändert.')
        return HttpResponseRedirect(self.success_url+url_args(request))


class BuerotageCancelView(MyUpdateView):
    permission_required = 'Einsatztage.change_buerotag'
    success_url = '/Einsatztage/buero/'
    model = Buerotag

    def get(self, request, pk):
        instance = get_object_or_404(Buerotag, pk=pk)
        koordinator = Koordinator.objects.filter(benutzer=request.user, team=instance.team).first()
        if instance.koordinator != koordinator:
            messages.error(
                request, self.model._meta.verbose_name.title() + ' am ' + str(instance.datum) + ' in ' +
                str(instance.team) + ' ist nicht auf Sie gebucht.')
        else:
            instance.koordinator = None
            instance.save()
            messages.success(request, self.model._meta.verbose_name.title() + ' "<a href="' + self.success_url +
                             str(instance.id) + '">' + str(instance.datum) + ' in ' + str(instance.team) +
                             '</a>" wurde erfolgreich geändert.')
        return HttpResponseRedirect(self.success_url+url_args(request))
