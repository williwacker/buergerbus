import datetime

from django.db import models
from django.utils import timezone

class Fahrtag(models.Model):
	datum      = models.DateField(blank=True)
	fahrer_vormittag     = models.ForeignKey('Team.Fahrer', related_name='vormittag', blank=True, null=True, on_delete=models.SET_NULL)
	fahrer_nachmittag    = models.ForeignKey('Team.Fahrer', related_name='nachmittag', blank=True, null=True, on_delete=models.SET_NULL)
	team       = models.ForeignKey('Einsatzmittel.Bus', null=True, on_delete=models.SET_NULL)
	archiv     = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.datum)

	class Meta():
		verbose_name_plural = "Fahrtage"
		verbose_name = "Fahrtag"

class Buerotag(models.Model):
	datum      = models.DateField(blank=True)
	mitarbeiter = models.ForeignKey('Team.Buerokraft', blank=True, null=True, on_delete=models.SET_NULL)
	team       = models.ForeignKey('Einsatzmittel.Buero', null=True, on_delete=models.SET_NULL)
	archiv     = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.datum)

	class Meta():
		verbose_name_plural = "Bürotage"
		verbose_name = "Bürotag"		