from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyListView, MyUpdateView,
                         MyView)
from Einsatzmittel.models import Buero
from Einsatzmittel.utils import get_buero_list

from ..filters import KoordinatorFilter
from ..forms import KoordinatorAddForm, KoordinatorChgForm
from ..models import Koordinator
from ..tables import KoordinatorTable

register = template.Library()


class KoordinatorView(MyListView):
    permission_required = 'Team.view_koordinator'
    model = Koordinator

    def get_fg_queryset(self):
        return Koordinator.objects.order_by('team', 'benutzer').filter(team__in=get_buero_list(self.request))

    def get_queryset(self):
        team = self.request.GET.get('team')
        sort = self.request.GET.get('sort')
        qs = self.get_fg_queryset()
        if team:
            qs = qs.filter(team=team)
        if sort:
            qs = qs.order_by(sort)
        return KoordinatorTable(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = KoordinatorFilter(self.request.GET, queryset=self.get_fg_queryset())
        return context


class KoordinatorAddView(MyCreateView):
    form_class = KoordinatorAddForm
    permission_required = 'Team.add_koordinator'
    success_url = '/Team/koordinator/'
    model = Koordinator

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form_class()
        form.fields['team'].queryset = Buero.objects.filter(id__in=get_buero_list(self.request))
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.aktiv:
            group = Group.objects.filter(name=instance.team).first()
            if group:
                instance.benutzer.groups.add(group)
        instance.created_by = self.request.user
        instance.save()
        self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'/'+url_args(self.request)+'">'+str(
            ", ".join([instance.benutzer.last_name, instance.benutzer.first_name]))+' '+str(instance.team)+'</a>" wurde erfolgreich hinzugefügt.'
        self.success_url += url_args(self.request)
        return super(KoordinatorAddView, self).form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)


class KoordinatorChangeView(MyUpdateView):
    form_class = KoordinatorChgForm
    permission_required = 'Team.change_koordinator'
    success_url = '/Team/koordinator/'
    model = Koordinator

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        instance = get_object_or_404(Koordinator, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        form.fields['name'].initial = ", ".join([instance.benutzer.last_name, instance.benutzer.first_name])
        form.fields['team'].queryset = Buero.objects.filter(id__in=get_buero_list(self.request))
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        if set(['team', 'aktiv']).intersection(set(form.changed_data)):
            old_group = Group.objects.filter(name=Buero.objects.get(pk=form.initial['team'])).first()
            if old_group:
                instance.benutzer.groups.remove(old_group)
            if instance.aktiv:
                group = Group.objects.filter(name=instance.team).first()
                if group:
                    instance.benutzer.groups.add(group)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(", ".join(
            [instance.benutzer.last_name, instance.benutzer.first_name]))+' '+str(instance.team)+'</a>" wurde erfolgreich geändert.'
        return super(KoordinatorChangeView, self).form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)


class KoordinatorCopyView(MyUpdateView):
    form_class = KoordinatorChgForm
    permission_required = 'Team.change_koordinator'
    success_url = '/Team/koordinator/'
    model = Koordinator

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        instance = get_object_or_404(Koordinator, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        form.fields['name'].initial = ", ".join([instance.benutzer.last_name, instance.benutzer.first_name])
        form.fields['team'].queryset = Buero.objects.filter(id__in=get_buero_list(self.request))
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_by = self.request.user
        if 'team' in form.changed_data:
            instance.pk = None
            instance.save()
            if instance.aktiv:
                group = Group.objects.filter(name=instance.team).first()
                if group:
                    instance.benutzer.groups.add(group)
            self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(", ".join(
                [instance.benutzer.last_name, instance.benutzer.first_name]))+' '+str(instance.team)+'</a>" wurde erfolgreich hinzugefügt.'
        return super(KoordinatorCopyView, self).form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)


class KoordinatorDeleteView(MyDeleteView):
    permission_required = 'Team.delete_koordinator'
    success_url = '/Team/koordinator/'
    model = Koordinator

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs['pk'])
        group = Group.objects.filter(name=instance.team).first()
        if group:
            instance.benutzer.groups.remove(group)
        messages.success(request, self.model._meta.verbose_name_raw+' "'+str(instance)+'" wurde gelöscht.')
        return self.delete(request, *args, **kwargs)
