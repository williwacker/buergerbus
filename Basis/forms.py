from django import forms
from django.contrib.auth.forms import UserChangeForm, UsernameField
from .models import MyUser, MyGroup
from django.forms import ModelForm
from django.shortcuts import render

from Basis.models import Document

class MyUserCreationForm(forms.ModelForm):
	"""
	A form that creates a user, with no privileges, from the given username and
	email address. Password will be generated-
	"""

	class Meta:
		model = MyUser
		fields = ('username', 'first_name', 'last_name', 'email')
		field_classes = {'username': UsernameField}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self._meta.model.USERNAME_FIELD in self.fields:
			self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True
		self.fields['email'].required = True

	def save(self, commit=True):
		user = super().save(commit=False)
		if commit:
			user.save()
		return user

class MyUserChangeForm(UserChangeForm):
	def __init__(self, *args, **kwargs):
		super(MyUserChangeForm, self).__init__(*args, **kwargs)

	class Meta:
		model = MyUser
		fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_staff', 'is_superuser', 'is_active']
		

class MyGroupChangeForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(MyGroupChangeForm, self).__init__(*args, **kwargs)

	class Meta:
		model = MyGroup
		fields = ['name', 'permissions']

class FeedbackForm(forms.Form):
	an = forms.CharField(required=False, label='An', widget=forms.HiddenInput(attrs={'readonly':'readonly','style':'width:800px;'}))
	betreff = forms.CharField(max_length=50, required=True, label='Betreff', widget=forms.TextInput(attrs={'style':'width:800px;'}))
	text = forms.CharField(max_length=400, required=False, label='Text', widget=forms.Textarea(attrs={'style':'width:800px;', 'autofocus':True}))

class DocumentAddForm(forms.ModelForm):

	class Meta:
		model = Document
		fields = ('description', 'document')
		widgets = {'description': forms.TextInput(attrs={'autofocus': True})}
		
	def __init__(self, *args, **kwargs):
		super(DocumentAddForm, self).__init__(*args, **kwargs)

	def clean(self):
		data = self.cleaned_data['document']
		if data.name[-4:].upper() != '.PDF':
			raise forms.ValidationError("Nur PDF Dokumente erlaubt")


class DocumentChangeForm(forms.ModelForm):
	document_ro = forms.CharField(required=False, label='Dokument', widget=forms.TextInput(attrs={'readonly':'readonly','style':'width:800px;'}))

	class Meta:
		model = Document
		fields = ('description', 'document_ro', )

	def __init__(self, *args, **kwargs):
		super(DocumentChangeForm, self).__init__(*args, **kwargs)
