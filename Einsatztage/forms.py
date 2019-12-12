from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from .models import Buerotag, Fahrtag


class FahrtagChgForm(ModelForm):

	class Meta:
		model = Fahrtag
		fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'urlaub']

	def __init__(self, *args, **kwargs):
		super(FahrtagChgForm, self).__init__(*args, **kwargs)
		self.fields['datum'].disabled = True
		self.fields['datum'].required = False
		self.fields['team'].disabled = True
		self.fields['team'].required = False

class BuerotagChgForm(ModelForm):

	class Meta:
		model = Buerotag
		fields = ['datum', 'team', 'koordinator', 'urlaub']

	def __init__(self, *args, **kwargs):
		super(BuerotagChgForm, self).__init__(*args, **kwargs)
		self.fields['datum'].disabled = True
		self.fields['datum'].required = False
		self.fields['team'].disabled = True
		self.fields['team'].required = False


class FahrplanEmailForm(forms.Form):
	von = forms.EmailField(required=False, widget=forms.HiddenInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	an = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	cc = forms.EmailField(required=False, help_text='Email Adressen mit ; trennen', widget=forms.TextInput(attrs={'style':'width:800px;'}))
	betreff = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	text = forms.CharField(max_length=400, required=False, widget=forms.Textarea(attrs={'style':'width:800px;'}))
	datei = forms.CharField(max_length=400, widget=forms.Textarea(attrs={'readonly':'readonly','style':'width:800px;'}), label='Datei(en)')
