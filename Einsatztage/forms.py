from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from .models import Buerotag, Fahrtag
from Team.models import Fahrer, Koordinator


class FahrtagChgForm(ModelForm):

	class Meta:
		model = Fahrtag
		fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'urlaub']
		widgets = {'datum' : forms.TextInput(attrs={'readonly':'readonly'})}

	def __init__(self, *args, **kwargs):
		super(FahrtagChgForm, self).__init__(*args, **kwargs)
		self.fields['team'].disabled = True
#		self.fields['team'].required = False

class BuerotagChgForm(ModelForm):

	class Meta:
		model = Buerotag
		fields = ['datum', 'team', 'koordinator', 'urlaub']
		widgets = {'datum' : forms.TextInput(attrs={'readonly':'readonly'})}

	def __init__(self, *args, **kwargs):
		super(BuerotagChgForm, self).__init__(*args, **kwargs)
		self.fields['team'].disabled = True
#		self.fields['team'].required = False


class FahrplanEmailForm(forms.Form):
	von = forms.EmailField(required=False, label='Von', widget=forms.HiddenInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	an = forms.CharField(required=False, label='An', widget=forms.TextInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	cc = forms.CharField(required=False, label='Cc', help_text='Email Adressen mit ; trennen', widget=forms.TextInput(attrs={'style':'width:800px;'}))
	betreff = forms.CharField(max_length=50, required=False, label='Betreff', widget=forms.TextInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	text = forms.CharField(max_length=400, required=False, label='Text', widget=forms.Textarea(attrs={'style':'width:800px;'}))
	datei = forms.CharField(max_length=400, label='Datei(en)', widget=forms.Textarea(attrs={'readonly':'readonly','style':'width:800px;'}))
