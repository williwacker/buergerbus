import datetime

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

class Fahrer(models.Model):
	name  = models.CharField(max_length=50)
	email = models.EmailField(max_length=254)
	telefon = models.CharField(max_length=30, null=True, blank=True)
	mobil = models.CharField(max_length=30, null=True, blank=True)
	team  = models.ForeignKey('Einsatzmittel.Bus', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True,help_text="Kann als Fahrer(in) eingeteilt werden")
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='update_fahrer', null=True, blank=True, on_delete=models.SET_NULL)
	def __str__(self):
		return self.name

	class Meta():
		verbose_name_plural = "Fahrer"
		verbose_name = "Fahrer"
		constraints = [models.UniqueConstraint(fields=['name','team'], name='unique_fahrer')]

class Koordinator(models.Model):
	benutzer = models.OneToOneField(User, related_name='benutzer2', on_delete=models.CASCADE)
	telefon = models.CharField(max_length=30, null=True, blank=True)
	mobil = models.CharField(max_length=30, null=True, blank=True)
	team  = models.ForeignKey('Einsatzmittel.Buero', null=True, on_delete=models.SET_NULL)
	aktiv = models.BooleanField(max_length=1, default=True,help_text="Kann als Koordinator(in) eingeteilt werden")
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='update_buero2', null=True, blank=True, on_delete=models.SET_NULL)

	def __str__(self):
		return ", ".join([str(self.benutzer.last_name),str(self.benutzer.first_name)])

	class Meta():
		verbose_name_plural = "Koordinatoren"
		verbose_name = "Koordinator"
		constraints = [models.UniqueConstraint(fields=['benutzer','team'], name='unique_koordinator')]