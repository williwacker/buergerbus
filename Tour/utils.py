from datetime import datetime, timedelta, time
import googlemaps
from django.conf import settings


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