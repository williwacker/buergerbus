from django.contrib.auth.views import PasswordChangeView
from django.views.generic import TemplateView

from Basis.utils import get_sidebar
from Basis.views import *


class MyPasswordChangeView(PasswordChangeView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        context['sidebar_liste'] = get_sidebar(self.request.user)
        return context


class MyPasswordChangeDoneView(TemplateView):
    template_name = 'registration/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_liste'] = get_sidebar(self.request.user)
        return context
