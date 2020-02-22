from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

class Kommunen(models.Model):
	name    	        = models.CharField(max_length=100, verbose_name = "Name")
	ansprechpartner     = models.CharField(max_length=100, verbose_name = "Ansprechpartner")
	telefon            	= models.CharField(max_length=30, blank=True, help_text="01234-1111")
	email 	   	        = models.EmailField(max_length=254, blank=True)
	use_google          = models.BooleanField(verbose_name = "Google Maps", help_text = "Google Maps verwenden")
	use_tour_hours      = models.BooleanField(verbose_name = "Fahrzeiten", help_text = "Bus Fahr-/Pausenzeiten berücksichtigen")
	googlemaps_key      = models.CharField(max_length=50, null=True, blank=True)
	subdir              = models.CharField(max_length=50, null=True, verbose_name = "Verzeichnis")
	send_dsgvo          = models.BooleanField(verbose_name = "DSGVO", help_text = "DSGVO verschicken")
	allow_outside_clients = models.BooleanField(verbose_name = "Fremde Fahrgäste", help_text = "Fahrgäste von ausserhalb der Kommune erlauben")
	portal_name         = models.CharField(max_length=50, default = "Bürgerbus Portal", verbose_name = "Titel")
	created_on 	        = models.DateTimeField(auto_now_add=True, null=True)
	created_by 	        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on 	        = models.DateTimeField(auto_now=True, null=True)
	updated_by 	        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	
	class Meta():
		verbose_name_plural = "Kommunen"
		verbose_name = "Kommune"
		ordering = ["name"]
		constraints = [models.UniqueConstraint(fields=['name'], name='unique_kommune')]

	def __str__(self):
		return str(self.name)

	def _permission_codename(self):
		# gibt den codenamen der entsprechenden Berechtigung zurück
		return  "Kommune_{}_editieren".format(self.id)

	def _permission_name(self):
		# gibt den beschreibenden Namen der entsprechenden Berechtigung zurück
		return "Kommune {} verwalten".format(self.name)

	def save(self, *args, **kwargs):
		# eigene save Methode, welche die Permission erzeugt für diese Kommune
		super().save(*args, **kwargs)
		content_type = ContentType.objects.get_for_model(self.__class__)
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID der Kommune und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.name = self._permission_name()
			permission.save()
		except Permission.DoesNotExist:
		# Falls es die Permission noch nicht gibt, erzeuge sie
			permission = Permission.objects.create(
				codename=self._permission_codename(),
				name=self._permission_name(),
				content_type=content_type)
		# Erzeuge die Gruppe passend zu dem Kommunennamen
		group, created = Group.objects.get_or_create(name=self.name)
		group.permissions.add(permission)


	def delete(self, *args, **kwargs):
		# eigene delete Methode, die die Permission wieder löscht, falls das
		# Kommune Objekt gelöscht wird
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID der Kommune und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.delete()
		except Permission.DoesNotExist:
			pass
		try:
		# Falls die Gruppe passend zu dem Kommunennamen existiert, so lösche sie
			group = Group.objects.get(name=self.name)
			group.delete()
		except:
			pass
		super().delete(*args, **kwargs)