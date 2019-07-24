import datetime

from django.db import models
from django.utils import timezone
from Team.models import Fahrer, Buerokraft
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
	def __str__(self):
		return str(self.datum)

#	def KlientenAnzahl(self):
#		from Tour.models import Tour
#		print(self.team)
#		return Tour.objects.filter(bus_id=self.team).count()

	class Meta():
		verbose_name_plural = "Fahrtage"
		verbose_name = "Fahrtag"

class Buerotag(models.Model):
	datum      = models.DateField(blank=True)
	team       = models.ForeignKey('Einsatzmittel.Buero', on_delete=models.CASCADE)	
#	mitarbeiter = models.ForeignKey('Team.Buerokraft', blank=True, null=True, on_delete=models.SET_NULL)
	mitarbeiter     = ChainedForeignKey(
        Buerokraft, # the model where you're populating your fahrer from
        chained_field="team", # the field on your own model that this field links to 
        chained_model_field="team", # the field on the foreign model this links to
		show_all=False,
        auto_choose=False,
		null=True,
		blank=True,
        sort=True)	
	archiv     = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.datum)

	class Meta():
		verbose_name_plural = "Bürotage"
		verbose_name = "Bürotag"		