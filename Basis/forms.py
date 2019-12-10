from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group
from Basis.models import Document


class MyUserChangeForm(UserChangeForm):
	def __init__(self, *args, **kwargs):
		super(MyUserChangeForm, self).__init__(*args, **kwargs)

	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_staff', 'is_superuser', 'is_active']

class MyGroupChangeForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(MyGroupChangeForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Group
		fields = ['name', 'permissions']

class FeedbackForm(forms.Form):
	von = forms.EmailField(required=False, widget=forms.HiddenInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	an = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'readonly':'readonly','style':'width:800px;'}))
#	cc = forms.EmailField(required=False, help_text='Email Adressen mit ; trennen', widget=forms.TextInput(attrs={'style':'width:800px;'}))
	betreff = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'style':'width:800px;'}))
	text = forms.CharField(max_length=400, required=False, widget=forms.Textarea(attrs={'style':'width:800px;'}))

class DocumentAddForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(DocumentAddForm, self).__init__(*args, **kwargs)

	def clean(self):
		data = self.cleaned_data['document']
		if data.name[-4:].upper() != '.PDF':
			raise forms.ValidationError("Nur PDF Dokumente erlaubt")

	class Meta:
		model = Document
		fields = ('description', 'document', )

class DocumentChangeForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(DocumentChangeForm, self).__init__(*args, **kwargs)

	dokument = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly','style':'width:800px;'}))

	class Meta:
		model = Document
		fields = ('description', 'dokument', )
