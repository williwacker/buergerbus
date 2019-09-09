import datetime

from django.forms import ModelForm
from django.db import models
from django.conf import settings
from django.utils import timezone
from Team.models import Fahrer, Koordinator
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey

class Fahrtag(models.Model):
	datum      = models.DateField(blank=True)
	team       = models.ForeignKey('Einsatzmittel.Bus', on_delete=models.CASCADE)
	fahrer_vormittag     = ChainedForeignKey(
		Fahrer, # the model where you're populating your fahrer from
		chained_field="team", # the field on your own model that this field links to 
		chained_model_field="team", # the field on the foreign model this links to
		show_all=False,
		auto_choose=False,
		null=True,
		blank=True,
		related_name='vormittag',
		sort=True)
	fahrer_nachmittag     = ChainedForeignKey(
		Fahrer, # the model where you're populating your fahrer from
		chained_field="team", # the field on your own model that this field links to 
		chained_model_field="team", # the field on the foreign model this links to
		show_all=False,
		auto_choose=False,
		null=True,
		blank=True,
		related_name='nachmittag',
		sort=True)		
	archiv     = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

	def __str__(self):
		return str(self.datum)
	
	@property
	def gaeste_nachmittag(self):
		from Tour.models import Tour
		return Tour.objects.filter(datum_id=self.id, uhrzeit__gte=datetime.time(12)).count()

	@property
	def gaeste_vormittag(self):
		from Tour.models import Tour
		return Tour.objects.filter(datum_id=self.id, uhrzeit__lt=datetime.time(12)).count()
#		gaeste_vormittag.short_description = _("Gäste vormittags")

	@property
	def wochentag(self):
		wochentage = ['Mo','Di','Mi','Do','Fr','Sa','So']
		return wochentage[self.datum.weekday()]

	class Meta():
		verbose_name_plural = "Fahrtage"
		verbose_name = "Fahrtag"

class Buerotag(models.Model):
	datum      = models.DateField(blank=True)
	team       = models.ForeignKey('Einsatzmittel.Buero', on_delete=models.CASCADE)	
	koordinator     = ChainedForeignKey(
		Koordinator, # the model where you're populating your fahrer from
		chained_field="team", # the field on your own model that this field links to 
		chained_model_field="team", # the field on the foreign model this links to
		show_all=False,
		auto_choose=False,
		null=True,
		blank=True,
		sort=True)	
	archiv     = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

	def __str__(self):
		return str(self.datum)

	@property
	def wochentag(self):
		wochentage = ['Mo','Di','Mi','Do','Fr','Sa','So']
		return wochentage[self.datum.weekday()]
		
	class Meta():
		verbose_name_plural = "Bürotage"
		verbose_name = "Bürotag"		