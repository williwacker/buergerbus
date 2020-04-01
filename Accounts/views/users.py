from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy

from Basis.utils import url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)

from ..forms import MyUserChangeForm, MyUserCreationForm
from ..models import MyUser
from ..tables import UserTable


class UserView(MyListView):
    permission_required = 'auth.view_user'
    model = MyUser

    def get_queryset(self):
        qs = self.model.objects.order_by('username')
        if not self.request.user.is_superuser:
            qs = qs.exclude(is_superuser=True)
        table = UserTable(qs)
        table.paginate(page=self.request.GET.get("page", 1), per_page=20)
        return table


class UserAddView(MyCreateView):
    permission_required = 'auth.add_user'
    form_class = MyUserCreationForm
    success_url = '/Accounts/benutzer/'
    model = MyUser

    def form_valid(self, form):
        user = form.save(commit=False)
        password = self.model.objects.make_random_password()
        user.set_password(password)
        user.created_by = self.request.user
        current_site = get_current_site(self.request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'username': user.username,
            'password': user._password,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain
        }
        email = EmailMessage(
            '[Bürgerbus] Ihr Benutzername',
            loader.render_to_string('registration/password_new_email.html', context),
            settings.DEFAULT_FROM_EMAIL,
            (user.email,),
        )
        email.send(fail_silently=False)
        user.save()
        self.success_url += url_args(self.request)
        self.success_message = self.model._meta.verbose_name.title(
        )+' "<a href="'+self.success_url+str(user.id)+'">'+user.username+'</a>" wurde erfolgreich angelegt.'
        return super(UserAddView, self).form_valid(form)


class UserChangeView(MyUpdateView):
    permission_required = 'auth.change_user'
    form_class = MyUserChangeForm
    model = MyUser
    success_url = '/Accounts/benutzer/'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        instance = get_object_or_404(self.model, pk=kwargs['pk'])
        form = self.form_class(instance=instance)
        if not self.request.user.is_superuser:
            # only the owned groups and user_permissions can be assigned
            form.fields['groups'].queryset = \
                form.fields['groups'].queryset.filter(id__in=[i.id for i in self.request.user.groups.all()])
            form.fields['user_permissions'].queryset = form.fields['user_permissions'].queryset.filter(
                id__in=[i.id for i in self.request.user.user_permissions.all()])
            form.fields['is_superuser'].widget = forms.HiddenInput()
            form.fields['is_staff'].widget = forms.HiddenInput()
            form.fields['password'].widget = forms.HiddenInput()
        context['form'] = form
        return render(request, self.template_name, context)

    def form_valid(self, form):
        instance = form.save()
        messages.success(
            self.request, 'Benutzer "<a href="' + self.success_url + str(instance.id) + '">' + instance.username +
            '</a>" wurde erfolgreich geändert.')
        return super(UserChangeView, self).form_valid(form)


class UserDeleteView(MyDeleteView):
    permission_required = 'auth.delete_user'
    success_url = '/Accounts/benutzer/'
    model = MyUser
