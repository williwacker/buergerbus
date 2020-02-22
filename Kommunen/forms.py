from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from Kommunen.models import Kommunen

class KommuneAddForm(ModelForm):
	class Meta:
		model = Kommunen
		fields = ['name', 'ansprechpartner', 'telefon', 'email', 'use_google', 'googlemaps_key', 'use_tour_hours', 'subdir',
				  'send_dsgvo', 'allow_outside_clients', 'portal_name']
		widgets = {'name': forms.TextInput(attrs={'autofocus': True}),'googlemaps_key': forms.TextInput(attrs={'style':'width:400px;'}),
				   'portal_name': forms.TextInput(attrs={'style':'width:400px;'}),
				   'email': forms.TextInput(attrs={'style':'width:400px;'})
				  }

class KommuneChgForm(ModelForm):
	class Meta:
		model = Kommunen
		fields = ['name', 'ansprechpartner', 'telefon', 'email', 'use_google', 'googlemaps_key', 'use_tour_hours', 'subdir',
				  'send_dsgvo', 'allow_outside_clients', 'portal_name']
		widgets = {'name': forms.TextInput(attrs={'readonly':'readonly'}),
				   'googlemaps_key': forms.TextInput(attrs={'style':'width:400px;'}),
				   'portal_name': forms.TextInput(attrs={'style':'width:400px;'}),
				   'email': forms.TextInput(attrs={'style':'width:400px;'})
				  }

	def __init__(self, *args, **kwargs):
		super(KommuneChgForm, self).__init__(*args, **kwargs)