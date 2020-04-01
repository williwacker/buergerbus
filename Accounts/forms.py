from django import forms
from django.contrib.auth.forms import UserChangeForm, UsernameField
from django.forms import ModelForm
from django.shortcuts import render

from .models import MyGroup, MyUser, Profile


class MyUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    email address. Password will be generated-
    """

    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class MyUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(MyUserChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MyUser
        fields = ['username', 'first_name', 'last_name', 'email', 'groups',
                  'user_permissions', 'is_staff', 'is_superuser', 'is_active']


class MyGroupChangeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyGroupChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MyGroup
        fields = ['name', 'permissions']


class MyProfileChangeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyProfileChangeForm, self).__init__(*args, **kwargs)
        self.fields['user'].disabled = True

    class Meta:
        model = Profile
        fields = ['user', 'telefon', 'mobil']
