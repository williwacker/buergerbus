from datetime import datetime, timedelta, time, date
import googlemaps
from django.conf import settings
from .models import Tour
from Einsatztage.models import Fahrtag
from Einsatzmittel.models import Bus
from Klienten.models import Klienten


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
			arrivaltime = (startuhrzeit + 
							timedelta(seconds=matrix['rows'][0]['elements'][0]['duration']['value']) +
							timedelta(minutes=settings.TRANSFER_TIME)).time()
		except:
			dist = "unbekannt"
			dura = "unbekannt"
			arrivaltime = time(0,0,0)

		return [dist,dura, arrivaltime]

# calculate earliest departure time from last arrival time
class DepartureTime():

	def time(self, cleaned_data):
		uhrzeit = cleaned_data['uhrzeit']
		datum   = cleaned_data['datum']
		bus     = cleaned_data['bus']
		bus_id  = Bus.objects.get(bus=bus)
		abholklient = cleaned_data['abholklient']
		abholklient_id = Klienten.objects.get(name=abholklient)
		instance = Tour.objects.order_by('uhrzeit').filter(bus=bus_id, datum=datum, uhrzeit__lt=uhrzeit).last()
		if instance and instance.ankunft:
			googleList = DistanceMatrix().getMatrix(
					instance.zielklient, 
					Klienten.objects.get(name=abholklient), 
					instance.datum.datum, 
					instance.ankunft)
			return googleList[2]
		return time(0,0,0)

# calculate earliest departure time when guest joins in from last start time
class JoinTime():

	def time(self, cleaned_data):
		uhrzeit = cleaned_data['uhrzeit']
		datum   = cleaned_data['datum']
		bus     = cleaned_data['bus']
		bus_id  = Bus.objects.get(bus=bus)
		abholklient = cleaned_data['abholklient']
		abholklient_id = Klienten.objects.get(name=abholklient)
		instance = Tour.objects.order_by('uhrzeit').filter(bus=bus_id, datum=datum, uhrzeit__lt=uhrzeit).last()
		if instance and instance.ankunft:
			googleList = DistanceMatrix().getMatrix(
					instance.abholklient, 
					Klienten.objects.get(name=abholklient), 
					instance.datum.datum, 
					instance.uhrzeit)
			return googleList[2]
		return time(0,0,0)		

class GuestCount():

	def get(self, cleaned_data):
		guest_count = int(cleaned_data['personenzahl'])
		uhrzeit = cleaned_data['uhrzeit']
		datum   = cleaned_data['datum']
		bus     = Bus.objects.get(bus=cleaned_data['bus'])
		zustieg = cleaned_data['zustieg']
		while zustieg:
			instance = Tour.objects.order_by('uhrzeit').filter(bus=bus, datum=datum, uhrzeit__lt=uhrzeit).last()
			guest_count += int(instance.personenzahl)
			zustieg = instance.zustieg
			uhrzeit = str(instance.uhrzeit)
		return guest_count

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