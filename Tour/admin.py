from django.contrib import admin
from django import forms

from Klienten.models import Klienten, Orte, Strassen
from Einsatztage.models import Fahrtag
from .models import Tour
from datetime import datetime, timedelta, time
import googlemaps

class DistanceMatrix():

	def setUp(self):
		self.key = 'AIzaSyAFnpYcStEl-LIKHKH1_5OIK0ghQKkECrw '
		self.client = googlemaps.Client(self.key)

	def getMatrix(self, o, d, startdatum, startzeit):

		origins      = [o.strasse.strasse+" "+o.hausnr+", "+o.ort.ort]
		destinations = [d.strasse.strasse+" "+d.hausnr+", "+d.ort.ort]
		startuhrzeit = datetime.combine(startdatum, startzeit)

		try:
			matrix = self.client.distance_matrix(origins, destinations, departure_time=startuhrzeit)

			dist  = matrix['rows'][0]['elements'][0]['distance']['text']
			dura  = matrix['rows'][0]['elements'][0]['duration']['text']
			arrivaltime = (startuhrzeit + timedelta(seconds=matrix['rows'][0]['elements'][0]['duration']['value'])).time()
		except:
			dist = "unbekannt"
			dura = "unbekannt"
			arrivaltime = time(0,0,0)

		return [dist,dura, arrivaltime]

#class KlientenInline(admin.TabularInline):
#	model = Klienten
#	fk_name = "klient"

class TourAdmin(admin.ModelAdmin):
	def abholort(self, obj):
		if (obj.klient == obj.abholklient):
			return ', '.join([obj.abholklient.ort.ort, obj.abholklient.strasse.strasse +" "+obj.abholklient.hausnr])
		else:
			return ', '.join([obj.abholklient.name, obj.abholklient.ort.ort, obj.abholklient.strasse.strasse +" "+obj.abholklient.hausnr])

	def zielort(self, obj):
		if (obj.klient == obj.zielklient):
			return ', '.join([obj.zielklient.ort.ort, obj.zielklient.strasse.strasse +" "+obj.zielklient.hausnr])
		else:
			return ', '.join([obj.zielklient.name, obj.zielklient.ort.ort, obj.zielklient.strasse.strasse +" "+obj.zielklient.hausnr])
	
	list_display = ('klient', 'bus', 'datum', 'uhrzeit', 'abholort', 'zielort', 'entfernung', 'ankunft')
	readonly_fields = ('entfernung','ankunft','bus')
	list_filter = ('datum','bus')
	list_editable = ('uhrzeit',)
	ordering = ('uhrzeit',)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "datum":
			kwargs["queryset"] = Fahrtag.objects.filter(archiv=False)
#		if db_field.name == 'team':
#			return BusChoiceField(queryset=Bus.objects.all())
		return super().formfield_for_foreignkey(db_field, request, **kwargs)
	
	def save_model(self, request, obj, form, change):
		# Entfernung und Fahrzeit aus GoogleMaps holen
		DM = DistanceMatrix()
		DM.setUp()
		googleList = DM.getMatrix(obj.abholklient, obj.zielklient, obj.datum.datum, obj.uhrzeit)
		obj.entfernung = googleList[0]
		obj.ankunft = googleList[2]
		# Bus nach Klientenort setzen
		obj.bus = obj.klient.ort.bus
		obj.user = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Tour, TourAdmin)
