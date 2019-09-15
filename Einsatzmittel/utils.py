from django.db import models
#from django.contrib.auth.models import Permission
from .models import Bus, Buero
from Basis.utils import has_perm

def get_bus_list(request):
	filterlist = []
	qs = Bus.objects.values_list('id', flat=True)
	for i in qs:
		codename = "Bus_{}_editieren".format(i)
		if has_perm(request.user,codename):
			filterlist.append(i)
	return filterlist

def get_buero_list(request):
	filterlist = []
	qs = Buero.objects.values_list('id', flat=True)
	for i in qs:
		codename = "Buero_{}_editieren".format(i)
		if has_perm(request.user,codename):
			filterlist.append(i)
	return filterlist