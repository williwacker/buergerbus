from django.forms import ModelForm
from django.shortcuts import render
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group


class MyUserChangeForm(UserChangeForm):
	def __init__(self, *args, **kwargs):
		super(MyUserChangeForm, self).__init__(*args, **kwargs)

	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_staff', 'is_superuser', 'is_active']

class MyGroupChangeForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(MyGroupChangeForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Group
		fields = ['name', 'permissions']
