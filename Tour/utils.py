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

		googleDict = {}
		try:
			matrix = self.client.distance_matrix(origins, destinations, departure_time=startuhrzeit)

			googleDict['distance'] = matrix['rows'][0]['elements'][0]['distance']['text']
			googleDict['duration_text'] = matrix['rows'][0]['elements'][0]['duration']['text']
			googleDict['duration_value'] = matrix['rows'][0]['elements'][0]['duration']['value']
			googleDict['arrivaltime'] = (startuhrzeit + 
							timedelta(seconds=matrix['rows'][0]['elements'][0]['duration']['value']) +
							timedelta(minutes=settings.TRANSFER_TIME)).time()
		except:
			googleDict['distance'] = ""
			googleDict['duration'] = ""
			googleDict['duration_value'] = 0
			googleDict['arrivaltime'] = time(0,0,0)

		return googleDict

# calculate earliest departure time from last arrival time
class DepartureTime():

	def time(self, cleaned_data):
		uhrzeit = cleaned_data['uhrzeit']
		datum   = cleaned_data['datum']
		bus     = cleaned_data['bus']
		bus_id  = Bus.objects.get(bus=bus)
		abholklient = cleaned_data['abholklient']
		instance = Tour.objects.order_by('uhrzeit').filter(bus=bus_id, datum=datum, uhrzeit__lt=uhrzeit).last()
		if instance and instance.ankunft and ('id' not in cleaned_data or instance.id != cleaned_data['id']):
			if cleaned_data['zustieg']:
				googleDict = DistanceMatrix().getMatrix(
					instance.abholklient, 
					abholklient, 
					instance.datum.datum, 
					instance.uhrzeit)
			else:
				googleDict = DistanceMatrix().getMatrix(
					instance.zielklient, 
					abholklient, 
					instance.datum.datum, 
					instance.ankunft)
			return googleDict['arrivaltime']
		return time(0,0,0)

# calculate latest departure time based on planned departure time of next customer
class Latest_DepartureTime():

	def time(self, cleaned_data):
		bus_id   = Bus.objects.get(bus=cleaned_data['bus'])
		instance = Tour.objects.order_by('uhrzeit').filter(bus=bus_id, datum=cleaned_data['datum'], uhrzeit__gt=cleaned_data['uhrzeit']).first()
		if instance and ('id' not in cleaned_data or instance.id != cleaned_data['id']):
			latest_departuretime = datetime.combine(instance.datum.datum, instance.uhrzeit)
			if instance.zustieg:
				# calculate time to next departure place
				googleDict = DistanceMatrix().getMatrix(
						cleaned_data['abholklient'],
						instance.abholklient,
						cleaned_data['datum'].datum, 
						cleaned_data['uhrzeit'])
				latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value'])).time()	
			else:
				# calculate time to destination
				googleDict = DistanceMatrix().getMatrix(
						cleaned_data['abholklient'],
						cleaned_data['zielklient'],
						cleaned_data['datum'].datum, 
						cleaned_data['uhrzeit'])
				latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))
				# calculate time back to next client departure place
				googleDict = DistanceMatrix().getMatrix(
						cleaned_data['zielklient'],
						instance.abholklient,
						instance.datum.datum, 
						instance.uhrzeit)
				latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value'])).time()
			return 	latest_departuretime
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