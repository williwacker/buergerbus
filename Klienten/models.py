import datetime

from django.db import models
from django.utils import timezone
from smart_selects.db_fields import ChainedForeignKey

DSGVO_AUSWAHL = [
	(None, 'Bitte Status auswählen'),
	('01', 'Neu'),
	('02', 'Versandt'),
	('03', 'Unterschrieben'),
	('99', 'Nicht notwendig'),
]

class Orte(models.Model):
	ort    = models.CharField(max_length=50)
	bus    = models.ForeignKey('Bus.Bus', null=True, on_delete=models.CASCADE)
	def __str__(self):
		return self.ort
	
	class Meta():
		verbose_name_plural = "Orte"
		verbose_name = "Ort"

class Strassen(models.Model):
	ort     = models.ForeignKey(Orte, null=True, on_delete=models.CASCADE)
	strasse = models.CharField(max_length=50)
	def __str__(self):
		return self.strasse

	class Meta():
		verbose_name_plural = "Strassen"
		verbose_name = "Strasse"


class Klienten(models.Model):
	name    = models.CharField(max_length=200)
	telefon = models.CharField(max_length=30)
	mobil   = models.CharField(max_length=30, null=True)
	ort     = models.ForeignKey(Orte, null=True, on_delete=models.CASCADE)
	strasse = ChainedForeignKey(
        Strassen,
        chained_field="ort",
        chained_model_field="ort",
		show_all=False,
        auto_choose=True,
        sort=True)
	hausnr  = models.CharField(max_length=10)
	dsgvo   = models.CharField(choices=DSGVO_AUSWAHL, max_length=2, blank=True, default='01'),
	bemerkung = models.CharField(max_length=200, blank=True, null=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return self.name

	class Meta():
		verbose_name_plural = "Klienten"
		verbose_name = "Klient"

