from datetime import datetime
from django import forms
from django.forms import ModelForm
from django.shortcuts import render
from django.core.exceptions import ValidationError

from .models import Buero, Bus
from Klienten.models import Klienten

class BusAddForm(ModelForm):
	class Meta:
		model = Bus
		fields = ['bus', 'plantage', 'sitzplaetze', 'fahrzeiten', 'email', 'standort', 'ignore_conflict', 'qr_code']
		widgets = {'bus': forms.TextInput(attrs={'autofocus': True})}
		
	def __init__(self, *args, **kwargs):
		super(BusAddForm, self).__init__(*args, **kwargs)
		self.fields['standort'].queryset = Klienten.objects.filter(typ='S')

class BusChgForm(ModelForm):
	class Meta:
		model = Bus
		fields = ['bus', 'plantage', 'sitzplaetze', 'fahrzeiten', 'email', 'standort', 'ignore_conflict', 'qr_code']
		
	def __init__(self, *args, **kwargs):
		super(BusChgForm, self).__init__(*args, **kwargs)
		self.fields['standort'].queryset = Klienten.objects.filter(typ='S')

class BueroAddForm(ModelForm):
	class Meta:
		model = Buero
		fields = ['buero', 'plantage' ,'buerotage', 'email']
		widgets = {'buero': forms.TextInput(attrs={'autofocus': True})}

class BueroChgForm(ModelForm):
	class Meta:
		model = Buero
		fields = ['buero', 'plantage' ,'buerotage', 'email']

	def __init__(self, *args, **kwargs):
		super(BueroChgForm, self).__init__(*args, **kwargs)		
