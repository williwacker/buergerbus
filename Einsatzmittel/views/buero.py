from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_relation_dict, get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyListView, MyUpdateView,
                         MyView)

from ..forms import BueroAddForm, BueroChgForm
from ..models import Buero
from ..tables import BueroTable
from ..utils import get_buero_list, get_bus_list

register = template.Library()


class BueroView(MyListView):
    permission_required = 'Einsatzmittel.view_buero'
    model = Buero

    def get_queryset(self):
        return(BueroTable(Buero.objects.order_by('buero').filter(id__in=get_buero_list(self.request))))


class BueroAddView(MyCreateView):
    form_class = BueroAddForm
    permission_required = 'Einsatzmittel.add_buero'
    success_url = '/Einsatzmittel/bueros/'
    model = Buero

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_liste'] = get_sidebar(self.request.user)
        context['title'] = "Büro hinzufügen"
        context['submit_button'] = "Sichern"
        context['back_button'] = ["Abbrechen", self.success_url+url_args(self.request)]
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()
        self.success_url += url_args(self.request)
        messages.success(
            self.request, 'Büro "<a href="' + self.success_url + str(instance.id) + '">' + instance.buero +
            '</a>" wurde erfolgreich hinzugefügt.')
        return super(BueroAddView, self).form_valid(form)


class BueroChangeView(MyUpdateView):
    permission_required = 'Einsatzmittel.change_buero'
    form_class = BueroChgForm
    model = Buero
    success_url = '/Einsatzmittel/bueros/'

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_by = self.request.user
        instance.save(force_update=True)
        self.success_url += url_args(self.request)
        messages.success(
            self.request, 'Büro "<a href="' + self.success_url + str(instance.id) + '">' + instance.buero +
            '</a>" wurde erfolgreich geändert.')
        return super(BueroChangeView, self).form_valid(form)


class BueroDeleteView(MyDeleteView):
    permission_required = 'Einsatzmittel.delete_buero'
    success_url = '/Einsatzmittel/bueros/'
    model = Buero
#    object_filter = [('id__in', 'get_buero_list(request)')]
    pass
