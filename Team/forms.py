from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from Klienten.forms import KlientenForm

from .models import Fahrer, Koordinator


class FahrerAddForm(KlientenForm):
	class Meta:
		model = Fahrer
		fields = ['name', 'team', 'email', 'telefon', 'mobil']

class FahrerChgForm(KlientenForm):

	class Meta:
		model = Fahrer
		fields = ['name', 'team', 'email', 'telefon', 'mobil', 'aktiv']

class KoordinatorAddForm(KlientenForm):

	class Meta:
		model = Koordinator
		fields = ['benutzer', 'team', 'telefon', 'mobil']

class KoordinatorChgForm(KlientenForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')

	class Meta:
		model = Koordinator
		fields = ['name', 'team', 'telefon', 'mobil', 'aktiv']
