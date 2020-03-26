from django.contrib import messages
from django.db.models import Max
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)

from ..forms import TopicAddForm
from ..models import Topic
from ..tables import TopicTable


class TopicView(MyListView):
    model = Topic
    permission_required = 'Faq.view_Topic'
    allow_empty = True

    def get_queryset(self):
        qs = Topic.objects.all()
        return TopicTable(qs)

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['sidebar_liste'] = get_sidebar(self.request.user)
        context['title'] = self.model._meta.verbose_name_plural
        if self.request.user.is_superuser:
            context['add'] = "Thema"
        context['url_args'] = url_args(self.request)
        return context


class TopicAddView(MyCreateView):
    form_class = TopicAddForm
    permission_required = 'Faq.add_topic'
    success_url = '/Faq/topics/admin/'
    model = Topic

    def get_context_data(self, **kwargs):
        context = super(TopicAddView, self).get_context_data(**kwargs)
        context['sidebar_liste'] = get_sidebar(self.request.user)
        context['title'] = self.model._meta.verbose_name_raw+" hinzufügen"
        context['submit_button'] = "Sichern"
        context['back_button'] = ["Abbrechen", self.success_url+url_args(self.request)]
        context['popup'] = self.request.GET.get('_popup', None)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_by = self.request.user
        instance.save()
        self.success_message = self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(
            instance.id)+'/'+url_args(self.request)+'">'+instance.name+'</a>" wurde erfolgreich hinzugefügt.'
        self.success_url += url_args(self.request)
        return super(TopicAddView, self).form_valid(form)


class TopicChangeView(MyUpdateView):
    permission_required = 'Faq.change_topic'
    form_class = TopicAddForm
    success_url = '/Faq/topics/admin/'
    model = Topic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model._meta.verbose_name_raw+" ändern"
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save(force_update=True)
        self.success_url += url_args(self.request)
        messages.success(self.request, self.model._meta.verbose_name_raw + ' "<a href="' + self.success_url +
                         str(instance.id) + '">' + str(instance) + '</a>" wurde erfolgreich geändert.')
        return super(TopicChangeView, self).form_valid(form)


class TopicDeleteView(MyDeleteView):
    permission_required = 'Faq.delete_topic'
    success_url = '/Faq/topics/admin/'
    model = Topic
    pass
