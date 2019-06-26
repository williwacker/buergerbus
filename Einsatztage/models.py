import datetime

from django.db import models
from django.utils import timezone

ZEIT_AUSWAHL = [
	(None, 'Bitte Tageszeit auswählen'),
	('Vormittag', 'Vormittag'),
	('Nachmittag', 'Nachmittag'),
]

class Einsatztag(models.Model):
	datum      = models.DateField(blank=True)
	fahrer_vormittag     = models.ForeignKey('Fahrerteam.Fahrer', related_name='vormittag', blank=True, null=True, on_delete=models.SET_NULL)
	fahrer_nachmittag    = models.ForeignKey('Fahrerteam.Fahrer', related_name='nachmittag', blank=True, null=True, on_delete=models.SET_NULL)
	team       = models.ForeignKey('Bus.Bus', null=True, on_delete=models.SET_NULL)
	feiertag   = models.BooleanField(default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.datum)

	class Meta():
		verbose_name_plural = "Einsatztage"
		verbose_name = "Einsatztag"