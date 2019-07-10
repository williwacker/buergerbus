import datetime

from django.db import models
from django.utils import timezone

class Fahrer(models.Model):
	name  = models.CharField(max_length=200)
	email = models.EmailField(max_length=254)
	mobil = models.CharField(max_length=30)
	team  = models.ForeignKey('Einsatzmittel.Bus', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return self.name

	class Meta():
		verbose_name_plural = "Fahrer"
		verbose_name = "Fahrer"

class Buerokraft(models.Model):
	name  = models.CharField(max_length=200)
	email = models.EmailField(max_length=254)
	mobil = models.CharField(max_length=30)
	team  = models.ForeignKey('Einsatzmittel.Buero', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return self.name

	class Meta():
		verbose_name_plural = "Bürokräfte"
		verbose_name = "Bürokraft"


