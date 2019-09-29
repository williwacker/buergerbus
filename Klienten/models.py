import datetime

from django.db import models
from django.utils import timezone
from django.conf import settings
from smart_selects.db_fields import ChainedForeignKey
from Einsatzmittel.models import Bus

DSGVO_AUSWAHL = [
	(None, 'Bitte Status auswählen'),
	('01', 'Neu'),
	('02', 'Versandt'),
	('03', 'Unterschrieben'),
#	('99', 'Nicht notwendig'),
]

TYP_AUSWAHL = [
	('F', 'Fahrgast'),
	('D', 'Dienstleister')
]

DIENSTLEISTER_AUSWAHL = [
	('Friseur', 'Friseur'),
	('Apotheke', 'Apotheke'),
	('Physio', 'Physio'),
	('Arzt', 'Arzt'),
]

class Orte(models.Model):
	ort    = models.CharField(max_length=50)
	bus    = models.ForeignKey('Einsatzmittel.Bus', null=True, blank=True, on_delete=models.CASCADE)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	
	def __str__(self):
		return self.ort
	
	class Meta():
		verbose_name_plural = "Orte"
		verbose_name = "Ort"
		ordering = ["ort"]

class Strassen(models.Model):
	ort     = models.ForeignKey(Orte, null=True, on_delete=models.CASCADE)
	strasse = models.CharField(max_length=50)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	
	def __str__(self):
		return self.strasse

	class Meta():
		verbose_name_plural = "Strassen"
		verbose_name = "Strasse"

class Klienten(models.Model):
	name    = models.CharField(max_length=200, help_text="Name, Vorname")
	name.short_description = "Name des Klienten"
	telefon = models.CharField(max_length=30, null=True, blank=True, help_text="01234-1111")
	mobil   = models.CharField(max_length=30, null=True, blank=True, help_text="0150-1111")
	ort     = models.ForeignKey(Orte, null=True, on_delete=models.CASCADE)
	bus     = models.ForeignKey('Einsatzmittel.Bus', null=True, blank=True, on_delete=models.CASCADE)
	strasse = ChainedForeignKey(
        Strassen, # the model where you're populating your streets from
        chained_field="ort", # the field on your own model that this field links to 
        chained_model_field="ort", # the field on Strassen that corresponds to ort
		show_all=False,
        auto_choose=True,
        sort=True
	)
	hausnr  = models.CharField(max_length=10)
	dsgvo   = models.CharField(choices=DSGVO_AUSWAHL, max_length=2, blank=True, default='01', verbose_name='DSGVO')
	typ     = models.CharField(choices=TYP_AUSWAHL, max_length=1, default='F') # F=Fahrgast, D=Dienstleister
	bemerkung = models.TextField(max_length=200, blank=True, null=True)
	kategorie = models.CharField(choices=DIENSTLEISTER_AUSWAHL,max_length=100, blank=True, null=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	
	def __str__(self):
		return self.name

	@property
	def vorname(self):
		try:
			nachname, vorname = self.name.split(',')
			return vorname.lstrip()
		except:
			return ''

	@property
	def nachname(self):
		try:
			nachname, vorname = self.name.split(',')
			return nachname
		except:
			return self.name		
	
	@property
	def name_ort(self):
		return "_".join([self.name, self.ort.ort])

	class Meta():
		verbose_name_plural = "Klienten"
		verbose_name = "Klient"