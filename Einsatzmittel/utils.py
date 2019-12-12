from django.db import models

from .models import Buero, Bus


def get_bus_list(request):
	filterlist = []
	qs = Bus.objects.values_list('id', flat=True)
	for i in qs:
		codename = "Einsatzmittel.Bus_{}_editieren".format(i)
		if request.user.has_perm(codename): filterlist.append(i)
	return filterlist

def get_buero_list(request):
	filterlist = []
	qs = Buero.objects.values_list('id', flat=True)
	for i in qs:
		codename = "Einsatzmittel.Buero_{}_editieren".format(i)
		if request.user.has_perm(codename): filterlist.append(i)
	return filterlist
