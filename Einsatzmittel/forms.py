from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from .models import Bus, Buero

class BusChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BusChgForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Bus
		fields = ['bus', 'sitzplaetze', 'fahrtage']

class BueroChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BueroChgForm, self).__init__(*args, **kwargs)
	class Meta:
		model = Buero
		fields = ['buero','buerotage']