from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey

from Einsatzmittel.models import Bus
from Einsatztage.models import Fahrtag


class Tour(models.Model):
	klient  = models.ForeignKey('Klienten.Klienten', related_name='klient', on_delete=models.CASCADE)
	bus    = models.ForeignKey('Einsatzmittel.Bus', related_name='bus2', on_delete=models.CASCADE)
	datum  = models.ForeignKey('Einsatztage.Fahrtag', related_name='datum2', on_delete=models.CASCADE)
	uhrzeit = models.TimeField(verbose_name="Abholzeit")
	abholklient  = models.ForeignKey('Klienten.Klienten', null=True, related_name='abholort', verbose_name="Wo",
		help_text="Bei wem soll der Fahrgast abgeholt werden?", on_delete=models.CASCADE)
	zielklient   = models.ForeignKey('Klienten.Klienten', null=True, related_name='zielort', verbose_name="Wohin",
		help_text="Zu wem soll der Fahrgast gebracht werden?" , on_delete=models.CASCADE)
	entfernung   = models.CharField(max_length=100, blank=True, null=True)
	ankunft      = models.TimeField(blank=True, null=True)
	bemerkung    = models.TextField(max_length=200, blank=True, null=True)
	personenzahl = models.IntegerField(default=1, verbose_name="Personen")
	zustieg      = models.BooleanField(default=False)
	konflikt     = models.TextField(max_length=200, blank=True, null=True)
	konflikt_richtung = models.CharField(max_length=2, blank=True, null=True)
	archiv       = models.BooleanField(default=False)
	created_on  = models.DateTimeField(auto_now_add=True, null=True)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+", on_delete=models.SET_NULL)
	updated_on  = models.DateTimeField(auto_now=True, blank=True, null=True)
	updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

	@property
	def abholort(self):
		if (self.klient == self.abholklient):
			return '\n'.join([self.abholklient.ort.ort, self.abholklient.strasse.strasse +" "+self.abholklient.hausnr])
		else:
			return '\n'.join([self.abholklient.name, self.abholklient.ort.ort, self.abholklient.strasse.strasse +" "+self.abholklient.hausnr, self.abholklient.telefon])

	@property
	def zielort(self):
		if (self.klient == self.zielklient):
			return '\n'.join([self.zielklient.ort.ort, self.zielklient.strasse.strasse +" "+self.zielklient.hausnr])
		else:
			return '\n'.join([self.zielklient.name, self.zielklient.ort.ort, self.zielklient.strasse.strasse +" "+self.zielklient.hausnr, self.zielklient.telefon])

	@property
	def fahrgast(self):
		return self.klient

	@property
	def is_today(self):
		return date.today() == self.datum.datum

	@property
	def has_markup_text(self):
		return len(set(settings.MARKUP_TEXT.lower().split(',')).intersection(set(self.bemerkung.lower().split()))) > 0

	@property
	def has_conflict(self):
		return self.konflikt != ''

	@property
	def hat_abhol_qr(self):
		if self.abholklient.latitude == 0: return False
		if self.abholklient.longitude == 0: return False
		return True	

	@property
	def hat_ziel_qr(self):
		if self.zielklient.latitude == 0: return False
		if self.zielklient.longitude == 0: return False
		return True						

	@property
	def alle_bemerkungen(self):
		list = []
		if self.klient.bemerkung: 			list.append(self.klient.bemerkung)
		if self.bemerkung: 					list.append(self.bemerkung)
		if self.klient != self.abholklient: list.append(self.abholklient.bemerkung)
		if self.klient != self.zielklient: 	list.append(self.zielklient.bemerkung)
		if list == [None]: 					list = ['']
		return '\n'.join(list)

	def einsatz_bus(self):
		rows = Fahrtag.objects.filter(datum=self.datum.datum).values_list('team',flat=True)
		einsatz_bus = [row for row in rows]
		return 'Bus '+str(einsatz_bus[0])

	@property	
	def datum_bus(self):
		return ' '.join([str(self.datum.datum), str(self.klient.bus)])

	@property
	def wochentag(self):
		wochentage = ['Mo','Di','Mi','Do','Fr','Sa','So']
		return wochentage[self.datum.weekday()]

	def klienten_bus(self):
		return str(self.klient.bus)

	def __unicode__(self):
		return self.name

	def __str__(self):
		return ' '.join([self.klient.name,str(self.klienten_bus()),str(self.datum),str(self.uhrzeit)])

	class Meta():
		verbose_name_plural = "Touren"
		verbose_name = "Tour"
		constraints = [models.UniqueConstraint(fields=['bus','datum','uhrzeit'], name='unique_tour')]
