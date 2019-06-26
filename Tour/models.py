from django.db import models

class Tour(models.Model):
	klient  = models.ForeignKey('Klienten.Klienten', related_name='klient', on_delete=models.CASCADE)
	bus     = models.ForeignKey('Bus.Bus', on_delete=models.CASCADE)
	datum   = models.ForeignKey('Einsatztage.Einsatztag', on_delete=models.CASCADE)
	uhrzeit = models.TimeField()
	abholklient  = models.ForeignKey('Klienten.Klienten', null=True, related_name='abholort', on_delete=models.CASCADE)
	zielklient  = models.ForeignKey('Klienten.Klienten', null=True, related_name='zielort', on_delete=models.CASCADE)
	bemerkung = models.CharField(max_length=200, blank=True, null=True)
	updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	def __str__(self):
		return ' '.join(['Bus:'+str(self.bus),str(self.uhrzeit),self.klient.name])

	class Meta():
		verbose_name_plural = "Touren"
		verbose_name = "Tour"