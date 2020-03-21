import datetime

from django.conf import settings
from django.db import models
from django.forms import ModelForm
from django.utils import timezone
from django.shortcuts import get_object_or_404
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey

from Team.models import Fahrer, Koordinator
from Tour.models import Tour


class Fahrtag(models.Model):
	datum      = models.DateField(blank=True)
	team       = models.ForeignKey('Einsatzmittel.Bus',on_delete=models.CASCADE)
	fahrer_vormittag  = models.ForeignKey(Fahrer, null=True, blank=True, related_name="+", verbose_name='Fahrer Vormittag', on_delete=models.SET_NULL)
	fahrer_nachmittag = models.ForeignKey(Fahrer, null=True, blank=True, related_name="+", verbose_name='Fahrer Nachmittag', on_delete=models.SET_NULL)	
	urlaub     = models.BooleanField(default=False)
	archiv     = models.BooleanField(default=False)
	created_on  = models.DateTimeField(auto_now_add=True, null=True)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

	class Meta():
		verbose_name_plural = "Fahrdienste"
		verbose_name = "Fahrdienst"
		constraints = [models.UniqueConstraint(fields=['datum','team'], name='unique_fahrtag')]

	def __str__(self):
		return str(self.datum)
	
	@property
	def gaeste_nachmittag(self):
		return Tour.objects.filter(datum_id=self.id, uhrzeit__gte=datetime.time(12)).count()

	@property
	def gaeste_vormittag(self):
		return Tour.objects.filter(datum_id=self.id, uhrzeit__lt=datetime.time(12)).count()

	@property
	def bookable_vormittag(self):
		return not self.fahrer_vormittag

	@property
	def bookable_nachmittag(self):
		return not self.fahrer_nachmittag		

	@property
	def wochentag(self):
		wochentage = ['Mo','Di','Mi','Do','Fr','Sa','So']
		return wochentage[self.datum.weekday()]

	@property
	def hat_fahrer(self):
		if self.gaeste_vormittag == 0 and self.gaeste_nachmittag == 0:
			return False
		if self.gaeste_vormittag > 0 and not self.fahrer_vormittag:
			return False
		if self.gaeste_nachmittag > 0 and not self.fahrer_nachmittag:
			return False
		return True
			

class Buerotag(models.Model):
	datum        = models.DateField(blank=True)
	team         = models.ForeignKey('Einsatzmittel.Buero', on_delete=models.CASCADE)	
	koordinator  = models.ForeignKey(Koordinator, null=True, blank=True, on_delete=models.SET_NULL)
	urlaub       = models.BooleanField(default=False)
	archiv       = models.BooleanField(default=False)
	created_on   = models.DateTimeField(auto_now_add=True, null=True)
	created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on   = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)
		
	class Meta():
		verbose_name_plural = "Bürodienste"
		verbose_name = "Bürodienst"
		constraints = [models.UniqueConstraint(fields=['datum','team'], name='unique_buerotag')]
		
	def __str__(self):
		return str(self.datum)

	@property
	def bookable(self):
		return not self.koordinator

	@property
	def wochentag(self):
		wochentage = ['Mo','Di','Mi','Do','Fr','Sa','So']
		return wochentage[self.datum.weekday()]
