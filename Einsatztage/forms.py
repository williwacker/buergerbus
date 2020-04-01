from django import forms
from django.forms import ModelForm
from django.shortcuts import render
from django.contrib.admin import widgets

from .models import Buerotag, Fahrtag
from Accounts.models import MyUser


class FahrtagAddForm(ModelForm):

    class Meta:
        model = Fahrtag
        fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'urlaub']
        widgets = {'datum': widgets.AdminDateWidget}

    def __init__(self, *args, **kwargs):
        super(FahrtagAddForm, self).__init__(*args, **kwargs)
        self.fields['datum'].required = True


class FahrtagChgForm(ModelForm):

    class Meta:
        model = Fahrtag
        fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'urlaub']
        widgets = {'datum': forms.TextInput(attrs={'readonly': 'readonly'})}

    def __init__(self, *args, **kwargs):
        super(FahrtagChgForm, self).__init__(*args, **kwargs)
        self.fields['team'].disabled = True


class BuerotagChgForm(ModelForm):

    class Meta:
        model = Buerotag
        fields = ['datum', 'team', 'koordinator', 'urlaub']
        widgets = {'datum': forms.TextInput(attrs={'readonly': 'readonly'})}

    def __init__(self, *args, **kwargs):
        super(BuerotagChgForm, self).__init__(*args, **kwargs)
        self.fields['team'].disabled = True


class FahrplanEmailForm(forms.Form):
    von = forms.EmailField(required=False, label='Von', widget=forms.HiddenInput(
        attrs={'readonly': 'readonly', 'style': 'width:800px;'}))
    an = forms.CharField(required=False, label='An', widget=forms.TextInput(
        attrs={'readonly': 'readonly', 'style': 'width:800px;'}))
    cc = forms.ModelMultipleChoiceField(MyUser.objects.all(), required=False, label='Cc', to_field_name='email')
    betreff = forms.CharField(max_length=50, required=False, label='Betreff', widget=forms.TextInput(
        attrs={'readonly': 'readonly', 'style': 'width:800px;'}))
    text = forms.CharField(max_length=400, required=False, label='Text',
                           widget=forms.Textarea(attrs={'style': 'width:800px;'}))
    datei = forms.CharField(max_length=400, label='Datei(en)', widget=forms.Textarea(
        attrs={'readonly': 'readonly', 'style': 'width:800px;'}))
