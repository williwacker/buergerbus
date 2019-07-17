from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from multiselectfield import MultiSelectField

BUS_TAGE_AUSWAHL = [
	(None, 'Bitte Bus-Fahrtage auswählen'),
	('Di,Do', 'Dienstag und Donnerstag'),
	('Mi,Fr', 'Mittwoch und Freitag'),
]

BUERO_TAGE_AUSWAHL = (
	(None, 'Bitte Bürotage auswählen'),
	('Mo,Di,Mi,Do', 'Montag, Dienstag, Mittwoch und Donnerstag'),
)

class Buero(models.Model):
	buero      = models.CharField(max_length=20)
	buerotage  = models.CharField(choices=BUERO_TAGE_AUSWAHL, max_length=20, default='')
	wird_verwaltet = models.BooleanField(max_length=1, default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.buero)

	class Meta():
		verbose_name_plural = "Büros"
		verbose_name = "Büro"

class Bus(models.Model):
	bus        = models.IntegerField(default=1, primary_key=True)
	fahrtage   = models.CharField(choices=BUS_TAGE_AUSWAHL, max_length=20, default='Di,Do')
	wird_verwaltet = models.BooleanField(max_length=1, default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return "Bus "+str(self.bus)
#		return str(self.bus)

	class Meta():
		verbose_name_plural = "Busse"
		verbose_name = "Bus"		
