import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from smart_selects.db_fields import ChainedForeignKey

from Einsatzmittel.models import Bus
from Klienten.utils import GeoLocation
from Tour.models import Tour

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
	plz    = models.CharField(max_length=5)
	bus    = models.ForeignKey('Einsatzmittel.Bus', null=True, blank=True, on_delete=models.CASCADE)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	
	class Meta():
		verbose_name_plural = "Orte"
		verbose_name = "Ort"
		ordering = ["ort"]
		constraints = [models.UniqueConstraint(fields=['ort'], name='unique_ort')]

	def __str__(self):
		return self.ort	

class Strassen(models.Model):
	ort     = models.ForeignKey(Orte, null=True, on_delete=models.CASCADE)
	strasse = models.CharField(max_length=50)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	
	class Meta():
		verbose_name_plural = "Strassen"
		verbose_name = "Strasse"
		constraints = [models.UniqueConstraint(fields=['ort','strasse'], name='unique_strasse')]

	def __str__(self):
		return self.strasse

class Klienten(models.Model):
	name    = models.CharField(max_length=100, help_text="Name, Vorname")
	name.short_description = "Name des Klienten"
	telefon = models.CharField(max_length=30, null=True, blank=True, help_text="01234-1111")
	mobil   = models.CharField(max_length=30, null=True, blank=True, help_text="0150-1111")
	ort     = models.ForeignKey(Orte, null=True, on_delete=models.CASCADE, verbose_name="Wohnort")
	bus     = models.ForeignKey('Einsatzmittel.Bus', null=True, blank=True, on_delete=models.CASCADE, 
				help_text="Dem Wohnort ist kein Bus zugeordnet. Deshalb für den Fahrgast einen Bus auswählen!")
	strasse = ChainedForeignKey(
        Strassen, # the model where you're populating your streets from
        chained_field="ort", # the field on your own model that this field links to 
        chained_model_field="ort", # the field on Strassen that corresponds to ort
		show_all=False,
        auto_choose=True,
        sort=True
	)
	hausnr  = models.CharField(max_length=10)
	dsgvo   = models.CharField(choices=DSGVO_AUSWAHL, max_length=2, blank=True, default='01', verbose_name='DSGVO Status')
	typ     = models.CharField(choices=TYP_AUSWAHL, max_length=1, default='F') # F=Fahrgast, D=Dienstleister
	bemerkung = models.TextField(max_length=200, blank=True, null=True)
	kategorie = models.CharField(choices=DIENSTLEISTER_AUSWAHL,max_length=100, blank=True, null=True)
	latitude = models.DecimalField(max_digits=7, decimal_places=4, default=0)
	longitude = models.DecimalField(max_digits=7, decimal_places=4, default=0)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

	class Meta():
		verbose_name_plural = "Klienten"
		verbose_name = "Klient"
		constraints = [models.UniqueConstraint(fields=['name','ort','strasse','hausnr'], name='unique_klient')]
	
	def clean(self):
		if not settings.ALLOW_OUTSIDE_CLIENTS \
		    and not self.ort.bus \
			and self.typ=='F': 
			raise ValidationError("Fahrgäste aus diesem Ort sind nicht erlaubt")

	def save(self, *args, **kwargs):
		if self.ort.bus != None and self.typ == 'F': self.bus=self.ort.bus
		if self.typ == 'D': self.dsgvo = '99'
		if self.latitude == 0: GeoLocation().getLocation(self)
		if not settings.ALLOW_OUTSIDE_CLIENTS \
		   	and not self.ort.bus \
			and self.typ=='F': 
			raise ValidationError("Fahrgäste aus diesem Ort sind nicht erlaubt")
		super(Klienten, self).save(*args, **kwargs)
	
	def __str__(self):
		if self.typ=='D':
			return " ".join([self.name, self.ort.ort, self.strasse.strasse])
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
		return " ".join([self.name, self.ort.ort])

	# Wie oft wurde der Dienstleister angefahren, oder von dort abgeholt ?
	@property
	def anzahl_dienstleister_touren(self):
		return Tour.objects.filter(zielklient_id=self.id).count()+Tour.objects.filter(abholklient_id=self.id).count()

	# Wie oft hat der Fahrgast gebucht ?
	@property
	def anzahl_fahrgast_touren(self):
		return Tour.objects.filter(klient_id=self.id).count()
