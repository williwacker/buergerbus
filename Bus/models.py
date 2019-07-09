from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

TAGE_AUSWAHL = [
	(None, 'Bitte Bus-Fahrtage auswählen'),
	('Di,Do', 'Dienstag und Donnerstag'),
	('Mi,Fr', 'Mittwoch und Freitag'),
]

class Bus(models.Model):
	bus_id     = models.IntegerField(default=1, primary_key=True)
	fahrtage   = models.CharField(choices=TAGE_AUSWAHL, max_length=5, default='Di,Do')
	wird_verwaltet = models.BooleanField(max_length=1, default=False)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.bus_id)

	class Meta():
		verbose_name_plural = "Busse"
		verbose_name = "Bus"		
