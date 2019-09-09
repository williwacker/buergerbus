from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from .models import Fahrtag, Buerotag

class FahrtagChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(FahrtagChgForm, self).__init__(*args, **kwargs)
		self.fields['datum'].disabled = True
		self.fields['datum'].required = False
		self.fields['team'].disabled = True
		self.fields['team'].required = False
	class Meta:
		model = Fahrtag
		fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag']

class BuerotagChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BuerotagChgForm, self).__init__(*args, **kwargs)
		self.fields['datum'].disabled = True
		self.fields['datum'].required = False
		self.fields['team'].disabled = True
		self.fields['team'].required = False
	class Meta:
		model = Buerotag
		fields = ['datum', 'team', 'koordinator']