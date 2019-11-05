from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from .models import Fahrer, Koordinator
from Klienten.forms import KlientenForm

class FahrerAddForm(KlientenForm):
	def __init__(self, *args, **kwargs):
		super(FahrerAddForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Fahrer
		fields = ['name', 'team', 'email', 'telefon', 'mobil']

class FahrerChgForm(KlientenForm):
	def __init__(self, *args, **kwargs):
		super(FahrerChgForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Fahrer
		fields = ['name', 'team', 'email', 'telefon', 'mobil', 'aktiv']

class KoordinatorAddForm(KlientenForm):
	def __init__(self, *args, **kwargs):
		super(KoordinatorAddForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Koordinator
		fields = ['benutzer', 'team', 'telefon', 'mobil']

class KoordinatorChgForm(KlientenForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')
	def __init__(self, *args, **kwargs):
		super(KoordinatorChgForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Koordinator
		fields = ['name', 'team', 'telefon', 'mobil', 'aktiv']		