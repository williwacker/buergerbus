from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from Basis.utils import get_relation_dict, get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyListView, MyUpdateView,
                         MyView)

from ..forms import BusAddForm, BusChgForm
from ..models import Bus
from ..tables import BusTable
from ..utils import get_bus_list

register = template.Library()


class BusView(MyListView):
    permission_required = 'Einsatzmittel.view_bus'
    model = Bus

    def get_queryset(self):
        return(BusTable(Bus.objects.order_by('bus').filter(id__in=get_bus_list(self.request))))


class BusAddView(MyCreateView):
    form_class = BusAddForm
    permission_required = 'Einsatzmittel.add_bus'
    success_url = '/Einsatzmittel/busse/'
    model = Bus

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()
        self.success_url += url_args(self.request)
        messages.success(
            self.request, 'Bus "<a href="' + self.success_url + str(instance.id) + '">' + instance.bus +
            '</a>" wurde erfolgreich hinzugefügt.')
        return super(BusAddView, self).form_valid(form)


class BusChangeView(MyUpdateView):
    permission_required = 'Einsatzmittel.change_bus'
    form_class = BusChgForm
    model = Bus
    success_url = '/Einsatzmittel/busse/'

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
        messages.success(self.request, self.model._meta.verbose_name_raw + ' "<a href="' + self.success_url +
                         str(instance.id) + '">' + str(instance) + '</a>" wurde erfolgreich geändert.')
        return super(BusChangeView, self).form_valid(form)


class BusDeleteView(MyDeleteView):
    permission_required = 'Einsatzmittel.delete_bus'
    model = Bus
    success_url = '/Einsatzmittel/busse/'
    pass
