from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from .models import Buero, Bus


class BusChgForm(ModelForm):

	class Meta:
		model = Bus
		fields = ['bus', 'plantage', 'sitzplaetze', 'fahrtage', 'email']
		
	def __init__(self, *args, **kwargs):
		super(BusChgForm, self).__init__(*args, **kwargs)



class BueroChgForm(ModelForm):
		
	class Meta:
		model = Buero
		fields = ['buero','buerotage']

	def __init__(self, *args, **kwargs):
		super(BueroChgForm, self).__init__(*args, **kwargs)		
