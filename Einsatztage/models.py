import datetime

from django.db import models
from django.utils import timezone
from Team.models import Fahrer, Buerokraft
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey

class Fahrtag(models.Model):
	datum      = models.DateField(blank=True)
	team       = models.ForeignKey('Einsatzmittel.Bus', on_delete=models.CASCADE)
	fahrer_vormittag     = models.ForeignKey(Fahrer, related_name='vormittag', blank=True, null=True, on_delete=models.SET_NULL)
#	fahrer_vormittag     = GroupedForeignKey(Fahrer, 'team')
#	fahrer_vormittag     = ChainedForeignKey(
#        Fahrer, # the model where you're populating your fahrer from
#        chained_field="team", # the field on your own model that this field links to 
#        chained_model_field="team", # the field on the foreign model this links to
#		show_all=True,
#        auto_choose=True,
#        sort=True)
	fahrer_nachmittag    = models.ForeignKey(Fahrer, related_name='nachmittag', blank=True, null=True, on_delete=models.SET_NULL)
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
	team       = models.ForeignKey('Einsatzmittel.Buero', on_delete=models.CASCADE)
	archiv     = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.datum)

	class Meta():
		verbose_name_plural = "Bürotage"
		verbose_name = "Bürotag"		