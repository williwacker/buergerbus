from datetime import datetime
from django import forms
from django.forms import ModelForm
from django.shortcuts import render
from django.core.exceptions import ValidationError

from .models import Buero, Bus
from Klienten.models import Klienten

class BusForm(ModelForm):
	def clean_planzeiten(self):
		planzeiten = self.cleaned_data['planzeiten']
		ranges = planzeiten.split(',')
		for range in ranges:
			timestamps = range.split('-')
			for timestamp in timestamps:
				try:
					time_obj = datetime.strptime(timestamp.strip(), '%H:%M')
				except ValueError:
					raise ValidationError("Ungültiges Format: {}".format(timestamp.strip()))
		# Always return a value to use as the new cleaned data, even if
		# this method didn't change it.
		return planzeiten

class BusAddForm(BusForm):
	class Meta:
		model = Bus
		fields = ['bus', 'plantage', 'sitzplaetze', 'fahrtage', 'email', 'planzeiten', 'standort']
		widgets = {'bus': forms.TextInput(attrs={'autofocus': True})}
		
	def __init__(self, *args, **kwargs):
		super(BusAddForm, self).__init__(*args, **kwargs)
		self.fields['standort'].queryset = Klienten.objects.filter(typ='S')

class BusChgForm(BusForm):
	class Meta:
		model = Bus
		fields = ['bus', 'plantage', 'sitzplaetze', 'fahrtage', 'email', 'planzeiten', 'standort']
		
	def __init__(self, *args, **kwargs):
		super(BusChgForm, self).__init__(*args, **kwargs)
		self.fields['standort'].queryset = Klienten.objects.filter(typ='S')

class BueroAddForm(ModelForm):
	class Meta:
		model = Buero
		fields = ['buero','buerotage', 'email']
		widgets = {'buero': forms.TextInput(attrs={'autofocus': True})}

class BueroChgForm(ModelForm):
	class Meta:
		model = Buero
		fields = ['buero','buerotage', 'email']

	def __init__(self, *args, **kwargs):
		super(BueroChgForm, self).__init__(*args, **kwargs)		
