from django.db import models
from django.core.exceptions import ValidationError
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey
import datetime

from Einsatzmittel.models import Bus
from Einsatztage.models import Fahrtag
from Klienten.models import Klienten, Orte, KlientenBus

class Tour(models.Model):
	klient  = models.ForeignKey('Klienten.Klienten', related_name='klient', on_delete=models.CASCADE)
	bus     = ChainedForeignKey(
		KlientenBus, # the model where you're populating your instances from
		chained_field="klient", # the field on your own model that this field links to 
		chained_model_field="name", # the field on the model above that corresponds to the chained field
		show_all=False, 
		null=False,
        auto_choose=False
	)
	datum = ChainedForeignKey(
        Fahrtag, # the model where you're populating your streets from
        chained_field="bus", # the field on your own model that this field links to 
        chained_model_field="team", # the field on Einsatztag that corresponds to bus_id
		show_all=False,
        auto_choose=True,
        sort=True)
	uhrzeit = models.TimeField()
	abholklient  = models.ForeignKey('Klienten.Klienten', null=True, related_name='abholort', on_delete=models.CASCADE)
	zielklient  = models.ForeignKey('Klienten.Klienten', null=True, related_name='zielort', on_delete=models.CASCADE)
	entfernung = models.CharField(max_length=100, blank=True, null=True)
	ankunft = models.TimeField(blank=True, null=True)
	bemerkung = models.TextField(max_length=200, blank=True, null=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)

	def klienten_bus(self):
		return self.klient.bus

	def einsatz_bus(self):
		rows = Fahrtag.objects.filter(datum=self.datum.datum).values_list('team',flat=True)
		einsatz_bus = [row for row in rows]
		return einsatz_bus[0]

	def __str__(self):
		return ' '.join([self.klient.name,'Bus:'+str(self.klienten_bus()),str(self.datum),str(self.uhrzeit)])

	def clean(self):
		
		if (self.einsatz_bus() != self.klienten_bus()):
			raise ValidationError(" ".join(['Bus', str(self.klienten_bus()), 'verkehrt an diesem Tag nicht']))

	class Meta():
		verbose_name_plural = "Touren"
		verbose_name = "Tour"

