import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Fahrer(models.Model):
	name  = models.CharField(max_length=50, help_text="Name, Vorname")
	email = models.EmailField(max_length=254)
	telefon = models.CharField(max_length=30, blank=True, help_text="01234-1111")
	mobil = models.CharField(max_length=30, blank=True, null=True, help_text="0150-1111")
	team  = models.ForeignKey('Einsatzmittel.Bus', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True, help_text="Kann als Fahrer(in) eingeteilt werden")
	created_on  = models.DateTimeField(auto_now_add=True, null=True)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

	class Meta():
		verbose_name_plural = "Fahrer(innen)"
		verbose_name = "Fahrer(in)"
		constraints = [models.UniqueConstraint(fields=['name','team'], name='unique_fahrer')]

	def __str__(self):
		return self.name

class Koordinator(models.Model):
	benutzer = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
	telefon = models.CharField(max_length=30, blank=True)
	mobil = models.CharField(max_length=30, blank=True, null=True)
	team  = models.ForeignKey('Einsatzmittel.Buero', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True, help_text="Kann als Koordinator(in) eingeteilt werden")
	created_on  = models.DateTimeField(auto_now_add=True, null=True)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

	class Meta():
		verbose_name_plural = "Koordinator(inn)en"
		verbose_name = "Koordinator(in)"
		constraints = [models.UniqueConstraint(fields=['benutzer','team'], name='unique_koordinator')]

	def __str__(self):
		return ", ".join([str(self.benutzer.last_name),str(self.benutzer.first_name)])
