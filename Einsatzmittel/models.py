from datetime import datetime, time, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import DEFERRED
from django.utils import timezone


class Wochentage(models.Model):
	name = models.CharField(max_length=10, unique=True, verbose_name = "Wochentag")

	class Meta():
		verbose_name_plural = "Wochentage"
		verbose_name = "Wochentag"
		ordering = ["id"]	

	def __str__(self):
		return self.name

	def kurzname(self):
		return self.name[:2]

class Fahrzeiten(models.Model):
	tag    = models.ForeignKey(Wochentage, null=True, on_delete=models.CASCADE, verbose_name = "Fahrtag")
	zeiten = models.CharField(max_length=50, default='08:00-12:00+14:00-17:00', verbose_name = "Fahrzeiten")

	class Meta():
		verbose_name_plural = "Fahrzeiten"
		verbose_name = "Fahrzeit"
		ordering = ["id"]	

	def __str__(self):
		return str(" ".join([self.tag.name,self.zeiten]))

class Buero(models.Model):
	buero      	= models.CharField(max_length=20, unique=True, verbose_name = "Büro")
	buerotage  	= models.ManyToManyField(Wochentage, default='', verbose_name = "Bürotage")
	email 	   	= models.EmailField(max_length=254, blank=True)
	plantage    = models.IntegerField(default=settings.COUNT_OFFICE_DAYS, verbose_name="Planbare Kalendertage")
	created_on 	= models.DateTimeField(auto_now_add=True, null=True)
	created_by 	= models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on 	= models.DateTimeField(auto_now=True, null=True)
	updated_by 	= models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	
	class Meta():
		verbose_name_plural = "Büros"
		verbose_name = "Büro"
		ordering = ["buero"]

	def __str__(self):
		return str(self.buero)

	@property
	def plan_ende(self):
		return (datetime.now()+timedelta(self.plantage)).strftime('%Y-%m-%d')

	def _permission_codename(self):
		# gibt den codenamen der entsprechenden Berechtigung zurück
		return  "Buero_{}_editieren".format(self.id)

	def _permission_name(self):
		# gibt den beschreibenden Namen der entsprechenden Berechtigung zurück
		return "Büro {} verwalten".format(self.buero)

	def save(self, *args, **kwargs):
		# eigene save Methode, welche die Permission erzeugt für diesen Bus
		super().save(*args, **kwargs)
		content_type = ContentType.objects.get_for_model(self.__class__)
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID des Büros und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.name = self._permission_name()
			permission.save()
		except Permission.DoesNotExist:
		# Falls es die Permission noch nicht gibt, erzeuge sie
			permission = Permission.objects.create(
				codename=self._permission_codename(),
				name=self._permission_name(),
				content_type=content_type)

	def delete(self, *args, **kwargs):
		# eigene delete Methode, die die Permission wieder löscht, falls das
		# Büro Objekt gelöscht wird
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID des Busses und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.delete()
		except Permission.DoesNotExist:
			pass
		super().delete(*args, **kwargs)

class Bus(models.Model):
	bus         = models.CharField(max_length=25, unique=True, verbose_name="Bus")
	sitzplaetze = models.IntegerField(default=8, verbose_name="Sitzplätze") 
	email 		= models.EmailField(max_length=254, blank=True)
	plantage    = models.IntegerField(default=settings.COUNT_TOUR_DAYS, verbose_name="Planbare Kalendertage")
	fahrzeiten  = models.ManyToManyField(Fahrzeiten, default='')
	standort    = models.ForeignKey('Klienten.Klienten', null=True, related_name="+", verbose_name="Bus Standort",
		on_delete=models.SET_NULL)
	ignore_conflict = models.BooleanField(default=False, verbose_name="Konflikte ignorieren")
	qr_code     = models.BooleanField(default=True, verbose_name="Fahrplan mit QR Code")
	created_on  = models.DateTimeField(auto_now_add=True, null=True)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

	class Meta():
		verbose_name_plural = "Busse"
		verbose_name = "Bus"
		ordering = ["bus"]

	def __str__(self):
		return str(self.bus)

	@property
	def plan_ende(self):
		return (datetime.now()+timedelta(self.plantage)).strftime('%Y-%m-%d')

	def _permission_codename(self):
		# gibt den codenamen der entsprechenden Berechtigung zurück
		return  "Bus_{}_editieren".format(self.id)

	def _permission_name(self):
		# gibt den beschreibenden Namen der entsprechenden Berechtigung zurück
		return "{} verwalten".format(self.bus)

	def save(self, *args, **kwargs):
		# eigene save Methode, welche die Permission erzeugt für diesen Bus
		super().save(*args, **kwargs)
		content_type = ContentType.objects.get_for_model(self.__class__)
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID des Busses und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.name = self._permission_name()
			permission.save()
		except Permission.DoesNotExist:
		# Falls es die Permission noch nicht gibt, erzeuge sie
			permission = Permission.objects.create(
				codename=self._permission_codename(),
				name=self._permission_name(),
				content_type=content_type)

	def delete(self, *args, **kwargs):
		# eigene delete Methode, die die Permission wieder löscht, falls das
		# Bus Objekt gelöscht wird
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID des Busses und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.delete()
		except Permission.DoesNotExist:
			pass
		super().delete(*args, **kwargs)
