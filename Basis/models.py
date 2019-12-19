import logging
import os
import datetime

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)

class Document(models.Model):
	document = models.FileField(upload_to='', verbose_name='Dokument')
	description = models.CharField(max_length=255, blank=True, verbose_name='Beschreibung')
	uploaded_on = models.DateTimeField(auto_now_add=True, verbose_name='hochgeladen am')
	uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='hochgeladen von',
		null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on = models.DateTimeField(auto_now=True, null=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
		null=True, related_name="+", on_delete=models.SET_NULL)


	class Meta():
		verbose_name = "Dokument"
		constraints = [models.UniqueConstraint(fields=['document'], name='unique_document')]
		
	def __str__(self):
		return str(self.document)

	@property
	def relative_path(self):
		return os.path.relpath(self.document.path, settings.MEDIA_ROOT)		



# These two auto-delete files from filesystem when they are unneeded:

@receiver(models.signals.post_delete, sender=Document)
def auto_delete_file_on_delete(sender, instance, **kwargs):
	"""
	Deletes file from filesystem
	when corresponding `Document` object is deleted.
	"""
	if instance.document.file:
		if os.path.isfile(instance.document.file.name):
			try:
				os.remove(instance.document.file.name)
			except:
				logger.info("{}: Error while deleting file {}".format(__name__, instance.document.file.name))

'''
@receiver(models.signals.pre_save, sender=Document)
def auto_delete_file_on_change(sender, instance, **kwargs):
	"""
	Deletes old file from filesystem
	when corresponding `Document` object is updated
	with new file.
	"""
	if not instance.pk:
		return False

	try:
		old_file = Document.objects.get(pk=instance.pk).file
	except Document.DoesNotExist:
		return False

	new_file = instance.document.file
	if not old_file == new_file:
		if os.path.isfile(old_file.name):
			try:
				os.remove(old_file.name)
			except:
				logger.info("{}: Error while deleting file {}".format(__name__, old_file.name))
'''