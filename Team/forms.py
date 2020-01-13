from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from Klienten.forms import KlientenForm

from .models import Fahrer, Koordinator


class FahrerAddForm(KlientenForm):
	class Meta:
		model = Fahrer
		fields = ['benutzer', 'team', 'telefon', 'mobil']

class FahrerChgForm(KlientenForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')

	class Meta:
		model = Fahrer
		fields = ['benutzer', 'name', 'team', 'telefon', 'mobil', 'aktiv']
		widgets = {'benutzer': forms.HiddenInput()}

	def __init__(self, *args, **kwargs):
		super(FahrerChgForm, self).__init__(*args, **kwargs)


class KoordinatorAddForm(KlientenForm):

	class Meta:
		model = Koordinator
		fields = ['benutzer', 'team', 'telefon', 'mobil']

class KoordinatorChgForm(KlientenForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')

	class Meta:
		model = Koordinator
		fields = ['name', 'team', 'telefon', 'mobil', 'aktiv']

	def __init__(self, *args, **kwargs):
		super(KoordinatorChgForm, self).__init__(*args, **kwargs)
