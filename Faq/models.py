import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from .managers import QuestionManager, QuestionQuerySet


class Topic(models.Model):
	"""
	Generic Topics for FAQ question grouping
	"""
	name = models.CharField(_('Thema'), max_length=150)
	sort_order = models.IntegerField(_('Sortierung'), default=0, 
		help_text=_('Reihenfolge der Themen.'))

	class Meta:
		verbose_name = _("Fragen und Antworten Thema")
		verbose_name_plural = _("Fragen und Antworten Themen")
		ordering = ['sort_order', 'name']

	def __str__(self):
		return self.name

	def _permission_codename(self):
		# gibt den codenamen der entsprechenden Berechtigung zurück
		return  "Topic_{}_editieren".format(self.id)

	def _permission_name(self):
		# gibt den beschreibenden Namen der entsprechenden Berechtigung zurück
		return "{} verwalten".format(self.name)

	def save(self, *args, **kwargs):
		# eigene save Methode, welche die Permission erzeugt für diesen Bus
		super().save(*args, **kwargs)
		content_type = ContentType.objects.get_for_model(self.__class__)
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID des Topics und die ändert sich nicht
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
		# Topic Objekt gelöscht wird
		try:
		# Falls es die Permission schon gibt, aktualisiere den Namen
		# der codename enthält nur die ID des Topics und die ändert sich nicht
			permission = Permission.objects.get(codename=self._permission_codename())
			permission.delete()
		except Permission.DoesNotExist:
			pass
		super().delete(*args, **kwargs)



class Question(models.Model):
	HEADER = 2
	ACTIVE = 1
	INACTIVE = 0
	STATUS_CHOICES = (
		(ACTIVE,    _('Active')),
		(INACTIVE,  _('Inactive')),
#        (HEADER,    _('Group Header')),
	)

	text = models.TextField(_('Frage'), help_text=_('Die aktuelle Frage.'))
	answer = models.TextField(_('Antwort'), blank=True, help_text=_('Die mögliche Antwort.'))
	topic = models.ForeignKey(Topic, verbose_name=_('Thema'), related_name='questions', on_delete=models.CASCADE)
	status = models.IntegerField(_('status'),
		choices=STATUS_CHOICES, default=INACTIVE,
		help_text=_("Nur Fragen im Status 'Aktiv' werden angezeigt.  "
					"Fragen markiert als Gruppen Titel werden als solche behandelt."))
	protected = models.BooleanField(_('is protected'), default=False,
		help_text=_("Check wenn nur angemeldete Benutzer die Frage sehen dürfen"))
	sort_order = models.IntegerField(_('sort order'), default=0,
		help_text=_('Die Reihenfolge in der die Fragen angezeigt werden.'))
	created_on  = models.DateTimeField(auto_now_add=True, null=True)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)
	objects = QuestionQuerySet.as_manager()

	class Meta:
		verbose_name = _("Fragen und Antworten ")
		verbose_name_plural = _("Fragen und Antworten ")
		ordering = ['sort_order', 'created_on']

	def __str__(self):
		return self.text

	def get_absolute_url(self):
		return ('faq_question_detail', [self.topic.slug, self.slug])

	def clean(self):
		if self.is_active() and self.answer == '':
			raise ValidationError("Aktive Fragen müssen eine Antwort haben!")

	def is_header(self):
		return self.status == Question.HEADER

	def is_active(self):
		return self.status == Question.ACTIVE
