import datetime

from django.db import models
from django.utils import timezone
from django.conf import settings

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
	benutzer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
	mobil = models.CharField(max_length=30)
	team  = models.ForeignKey('Einsatzmittel.Buero', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return ", ".join([str(self.benutzer.last_name),str(self.benutzer.first_name)])

	class Meta():
		verbose_name_plural = "Bürokräfte"
		verbose_name = "Bürokraft"


