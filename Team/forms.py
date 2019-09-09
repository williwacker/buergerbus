from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from .models import Fahrer, Koordinator

class FahrerAddForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(FahrerAddForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Fahrer
		fields = ['name', 'team', 'email', 'telefon', 'mobil']

class FahrerChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(FahrerChgForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Fahrer
		fields = ['name', 'team', 'email', 'telefon', 'mobil', 'aktiv']

class KoordinatorAddForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(KoordinatorAddForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Koordinator
		fields = ['benutzer', 'team', 'telefon', 'mobil']

class KoordinatorChgForm(ModelForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')
	def __init__(self, *args, **kwargs):
		super(KoordinatorChgForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Koordinator
		fields = ['name', 'team', 'telefon', 'mobil', 'aktiv']		