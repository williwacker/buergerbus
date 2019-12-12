from datetime import datetime, time, timedelta

import googlemaps
from django.conf import settings
from django.contrib import admin

from Einsatzmittel.models import Bus
from Einsatztage.models import Fahrtag
from Klienten.models import Klienten, Orte, Strassen

from .models import Tour


class DistanceMatrix():

	def setUp(self):
		self.key = settings.GOOGLEMAPS_KEY
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

class TourAdmin(admin.ModelAdmin):

	list_display = ('klient', 'bus', 'datum', 'uhrzeit', 'abholort', 'zielort', 'entfernung', 'ankunft', 'updated_on')
	readonly_fields = ('entfernung','ankunft')
	list_filter = ('datum','bus')
	list_editable = ('uhrzeit',)
	ordering = ('datum','uhrzeit',)

	"""
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
	"""

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "datum":
			kwargs["queryset"] = Fahrtag.objects.filter(archiv=False)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def save_model(self, request, obj, form, change):
		# Entfernung und Fahrzeit aus GoogleMaps holen
		DM = DistanceMatrix()
		DM.setUp()
		googleList = DM.getMatrix(obj.abholklient, obj.zielklient, obj.datum.datum, obj.uhrzeit)
		obj.entfernung = googleList[0]
		obj.ankunft = googleList[2]
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)

class TourInline(admin.TabularInline):
    model = Tour
    inline_actions = []

    def has_add_permission(self):
        return False


admin.site.register(Tour, TourAdmin)
