from datetime import datetime, timedelta, time, date
import googlemaps
from django.conf import settings
from .models import Tour
from Einsatztage.models import Fahrtag


class DistanceMatrix():

	def __init__(self):
		self.setUp()

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

class TourArchive():

	def __init__(self):
		rows = Tour.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		for tag, id in existierende_tage:
			fahrtag = Fahrtag.objects.get(pk=tag)
			if fahrtag.datum < date.today():
				t = Tour.objects.get(pk=id)
				t.archiv=True
				t.save()		