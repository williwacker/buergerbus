from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from Klienten.forms import KlientenForm

from .models import Fahrer, Koordinator


class FahrerAddForm(KlientenForm):
	class Meta:
		model = Fahrer
		fields = ['benutzer', 'team', 'telefon', 'mobil']

	def clean(self):
		benutzer = self.cleaned_data['benutzer']
		if benutzer.first_name == '' \
		or benutzer.last_name == '':
			raise forms.ValidationError("Benutzer hat keinen Vornamen und/oder Nachnamen. Bitte durch den Administrator eintragen lassen!")

class FahrerChgForm(KlientenForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')

	class Meta:
		model = Fahrer
		fields = ['benutzer', 'name', 'team', 'telefon', 'mobil', 'aktiv']
		widgets = {'benutzer': forms.HiddenInput()}

	def __init__(self, *args, **kwargs):
		super(FahrerChgForm, self).__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super(FahrerChgForm, self).clean()
		benutzer = cleaned_data.get('benutzer')
		team     = cleaned_data.get('team')
		if Fahrer.objects.filter(benutzer=benutzer, team=team).exists():
			raise forms.ValidationError('Fahrer ist bereits für diesen Bus angelegt')


class KoordinatorAddForm(KlientenForm):

	class Meta:
		model = Koordinator
		fields = ['benutzer', 'team', 'telefon', 'mobil']

	def clean(self):
		benutzer = self.cleaned_data['benutzer']
		if benutzer.first_name == '' \
		or benutzer.last_name == '':
			raise forms.ValidationError("Benutzer hat keinen Vornamen und/oder Nachnamen. Bitte durch den Administrator eintragen lassen!")


class KoordinatorChgForm(KlientenForm):
	name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Name')

	class Meta:
		model = Koordinator
		fields = ['name', 'team', 'telefon', 'mobil', 'aktiv']

	def __init__(self, *args, **kwargs):
		super(KoordinatorChgForm, self).__init__(*args, **kwargs)
