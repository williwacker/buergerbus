import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
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
		verbose_name = _("FAQ Thema")
		verbose_name_plural = _("FAQ Themen")
		ordering = ['sort_order', 'name']

	def __str__(self):
		return self.name


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
		verbose_name = _("Häufig gestellte Frage")
		verbose_name_plural = _("Häufig gestellte Fragen")
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
