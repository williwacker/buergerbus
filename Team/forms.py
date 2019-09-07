from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from .models import Buerokraft, Fahrer

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

class BuerokraftAddForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BuerokraftAddForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Buerokraft
		fields = ['benutzer', 'team', 'telefon', 'mobil']

class BuerokraftChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BuerokraftChgForm, self).__init__(*args, **kwargs)
		self.fields['benutzer'].disabled = True
		self.fields['benutzer'].required = False

	class Meta:
		model = Buerokraft
		fields = ['benutzer', 'team', 'telefon', 'mobil', 'aktiv']		