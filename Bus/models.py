from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

TAGE_AUSWAHL = [
	(None, 'Bitte Bus-Fahrtage auswählen'),
	('Mo', 'Montag'),
	('Di', 'Dienstag'),
	('Mi', 'Mittwoch'),
	('Do', 'Donnerstag'),
	('Fr', 'Freitag'),
]

class Bus(models.Model):
	bus_id     = models.IntegerField(default=1, primary_key=True)
	fahrtage   = ArrayField(
		models.CharField(choices=TAGE_AUSWAHL, max_length=2, blank=True, default='Mo'),
    )
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return str(self.bus_id)

	class Meta():
		verbose_name_plural = "Busse"
		verbose_name = "Bus"		
