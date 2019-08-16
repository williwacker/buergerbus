from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from .models import Fahrtag, Buerotag

class FahrtagChgForm(ModelForm):
	class Meta:
		model = Fahrtag
		fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag']
		widgets = {'datum': forms.TextInput(attrs={'readonly': 'readonly'}),'team': forms.TextInput(attrs={'readonly': 'readonly'})}
