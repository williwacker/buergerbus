from django.db import models
from django.db.models import DEFERRED
from django.utils import timezone
from django.conf import settings
#from django.contrib.postgres.fields import ArrayField
#from multiselectfield import MultiSelectField
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
#from .utils import BusManager

TAGE_AUSWAHL = (
	(None, 'Bitte Einsatztag(e) auswählen'),
	('Mo,Di,Mi,Do', 'Montag, Dienstag, Mittwoch und Donnerstag'),
	('Di,Do', 'Dienstag und Donnerstag'),
	('Mi,Fr', 'Mittwoch und Freitag'),
	('Mo', 'Montag'),
	('Di', 'Dienstag'),
	('Mi', 'Mittwoch'),
	('Do', 'Donnerstag'),
	('Fr', 'Freitag'),	
)

class Buero(models.Model):
	buero      = models.CharField(max_length=20, verbose_name = "Büro")
	buerotage  = models.CharField(choices=TAGE_AUSWAHL, max_length=20, default='', verbose_name = "Bürotag")
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	
	def __str__(self):
		return str(self.buero)

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
			print(self._permission_codename())			
			permission.save()
		except Permission.DoesNotExist:
		# Falls es die Permission noch nicht gibt, erzeuge sie
			print(self._permission_codename())
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

	class Meta():
		verbose_name_plural = "Büros"
		verbose_name = "Büro"
		ordering = ["buero"]		

class Bus(models.Model):
	bus         = models.IntegerField(default=1, primary_key=True, verbose_name="Bus")
	sitzplaetze = models.IntegerField(default=8, verbose_name="Anzahl Sitzplätze") 
	fahrtage    = models.CharField(choices=TAGE_AUSWAHL, max_length=20, default='Di,Do', verbose_name="Fahrtag")
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

#	objects     = BusManager()
	
	def __str__(self):
		return "Bus "+str(self.bus)
#		return str(self.bus)

	def _permission_codename(self):
		# gibt den codenamen der entsprechenden Berechtigung zurück
		return  "Bus_{}_editieren".format(self.bus)

	def _permission_name(self):
		# gibt den beschreibenden Namen der entsprechenden Berechtigung zurück
		return "Bus {} verwalten".format(self.bus)

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

	class Meta():
		verbose_name_plural = "Busse"
		verbose_name = "Bus"
		ordering = ["bus"]
