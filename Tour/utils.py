import logging
from datetime import date, datetime, time, timedelta

import googlemaps
from django.conf import settings
from django.shortcuts import get_object_or_404

from Einsatzmittel.models import Bus
from Einsatztage.models import Fahrtag
from Klienten.models import Klienten

from .models import Tour

logger = logging.getLogger(__name__)

class DistanceMatrix():

	def __init__(self):
		self.setUp()

	def setUp(self):
		self.key = settings.GOOGLEMAPS_KEY
		self.client = googlemaps.Client(self.key)

	def get_form_data(self, form):
		googleDict = {}
		if settings.USE_GOOGLE:
			if 'entfernung' not in form.cleaned_data \
			or form.cleaned_data['entfernung'] == '' \
			or set(['abholklient','zielklient','datum','uhrzeit']).intersection(set(form.changed_data)):
				googleDict = self.getMatrix(
					form.cleaned_data['abholklient'], 
					form.cleaned_data['zielklient'], 
					form.cleaned_data['datum'].datum, 
					form.cleaned_data['uhrzeit'])
		return googleDict		

	def getMatrix(self, o, d, startdatum, startzeit):

		origins      = ["{} {}, {} {}".format(o.strasse.strasse,o.hausnr,o.ort.plz,o.ort.ort)]
		destinations = ["{} {}, {} {}".format(d.strasse.strasse,d.hausnr,d.ort.plz,d.ort.ort)]
		startuhrzeit = datetime.combine(startdatum, startzeit)
		logger.info("{}: origin={} destination={} start={}".format(__name__, origins, destinations, str(startuhrzeit)))

		googleDict = {}
		try:
			matrix = self.client.distance_matrix(origins, destinations, departure_time=startuhrzeit)

			googleDict['distance'] = matrix['rows'][0]['elements'][0]['distance']['text']
			googleDict['duration_text'] = matrix['rows'][0]['elements'][0]['duration']['text']
			googleDict['duration_value'] = matrix['rows'][0]['elements'][0]['duration']['value']
			if googleDict['duration_value'] <= 20:
				googleDict['duration_value'] = 0
				googleDict['arrivaltime'] = startuhrzeit.time()
			else:
				googleDict['arrivaltime'] = (startuhrzeit + 
							timedelta(seconds=googleDict['duration_value']) +
							timedelta(minutes=settings.TRANSFER_TIME)).time()
		except:
			googleDict['distance'] = ""
			googleDict['duration'] = ""
			googleDict['duration_value'] = 0
			googleDict['arrivaltime'] = time(0,0,0)

		return googleDict

# calculate earliest departure time from last arrival time
class DepartureTime():

	# get the nearest tour timeslot start time
	def get_timeslot_start(self, bus, weekday, abholzeit):
		if settings.USE_TOUR_HOURS:
			fahrzeiten = bus.fahrzeiten.filter(tag=weekday).values_list('zeiten', flat=True).first()
			if not fahrzeiten: return time(0,0)
			for fahrzeit in fahrzeiten.split('+'):
				start_end_zeiten = fahrzeit.split('-')
				if abholzeit < datetime.strptime(start_end_zeiten[1], '%H:%M').time():
					return datetime.strptime(start_end_zeiten[0], '%H:%M').time()
		return time(0,0)

	# iterate through all previous tours as long as there is a tour join
	# return the instance with the latest arrival time
	def get_previous_tour(self, instance): # instance is already the next previous tour
		ankunft = instance.ankunft
		return_instance = instance
		while instance.zustieg:
			instance = Tour.objects.order_by('uhrzeit').filter(bus=instance.bus.id, datum=instance.datum, uhrzeit__lt=instance.uhrzeit).last()
			if instance.ankunft > ankunft:
				return_instance = instance
		return return_instance


	def time(self, form):
		id      = form.cleaned_data.get('id',0)
		uhrzeit = form.cleaned_data.get('uhrzeit')
		datum   = form.cleaned_data.get('datum')
		bus     = form.cleaned_data.get('bus')
		bus_id  = Bus.objects.get(bus=bus)
		abholklient = form.cleaned_data['abholklient']
		instance = Tour.objects.order_by('uhrzeit').\
			filter(bus=bus_id, datum=datum, uhrzeit__lt=uhrzeit, uhrzeit__gte=self.get_timeslot_start(bus, datum.datum.isoweekday(), uhrzeit)).\
			exclude(id__in=[id]).last()
		if instance:
			if form.cleaned_data['zustieg']:
				googleDict = DistanceMatrix().getMatrix(
					instance.abholklient, 
					abholklient, 
					instance.datum.datum, 
					instance.uhrzeit)
			else:
#				logger.info('check driving time from last clients arrival time to this clients start time')
				instance = self.get_previous_tour(instance)
				googleDict = DistanceMatrix().getMatrix(
					instance.zielklient, 
					abholklient, 
					instance.datum.datum, 
					instance.ankunft)
			return googleDict['arrivaltime']
		# calculate earliest start time in the matching tour timeslot
		elif settings.USE_TOUR_HOURS:
#			logger.info('check start of tour is within the tour timeslot')
			googleDict = DistanceMatrix().getMatrix(
				bus.standort, 
				abholklient, 
				datum.datum, 
				self.get_timeslot_start(bus, datum.datum.isoweekday(), uhrzeit))
			return googleDict['arrivaltime']
		return time(0,0,0)

# calculate latest departure time based on planned departure time of next customer
class Latest_DepartureTime():

	# get the nearest tour timeslot end time
	def get_timeslot_end(self, bus, weekday, abholzeit):
		if settings.USE_TOUR_HOURS:
			fahrzeiten = bus.fahrzeiten.filter(tag=weekday).values_list('zeiten', flat=True).first()
			if not fahrzeiten: return time(23,59)
			for fahrzeit in fahrzeiten.split('+'):
				start_end_zeiten = fahrzeit.split('-')
				if abholzeit < datetime.strptime(start_end_zeiten[1], '%H:%M').time():
					return datetime.strptime(start_end_zeiten[1], '%H:%M').time()
		return time(23,59)	

	def time(self, form):
		id      = form.cleaned_data.get('id',0)
		uhrzeit = form.cleaned_data['uhrzeit']
		ankunft = form.cleaned_data['ankunft']
		datum   = form.cleaned_data['datum']
		bus     = form.cleaned_data['bus']
		bus_id  = Bus.objects.get(bus=form.cleaned_data['bus'])
		# calculate latest departure time in order to match the end of the tour timeslot
		if settings.USE_TOUR_HOURS:
			latest_arrivaltime = self.get_timeslot_end(bus, datum.datum.isoweekday(), uhrzeit)
			timediff = (datetime.combine(datum.datum, latest_arrivaltime) - datetime.combine(datum.datum, uhrzeit)).total_seconds()
			if timediff < 3600:		# 1h
				logger.info('check end of tour is within the tour timeslot')
				googleDict = DistanceMatrix().getMatrix(
					form.cleaned_data['zielklient'], 
					bus.standort, 
					datum.datum, 
					ankunft)
				if googleDict['arrivaltime'] > latest_arrivaltime:
					overtime = (datetime.combine(datum.datum, googleDict['arrivaltime']) - datetime.combine(datum.datum, latest_arrivaltime)).total_seconds()
					latest_departuretime = (datetime.combine(datum.datum, uhrzeit) - timedelta(seconds=overtime)).time()
					return 	latest_departuretime
		# calculate latest departure time for the next client
		instance = Tour.objects.order_by('uhrzeit').filter(
			bus=bus_id, datum=datum, uhrzeit__gt=uhrzeit).exclude(id__in=[id]).first()
		if instance:
#			logger.info('check driving time from this clients arrival to start time of next client')
			latest_departuretime = datetime.combine(instance.datum.datum, instance.uhrzeit)
			if instance.zustieg:
				# calculate time to next departure place
				logger.info('calculate time to next departure place joining in')
				googleDict = DistanceMatrix().getMatrix(
						form.cleaned_data['abholklient'],
						instance.abholklient,
						datum.datum, 
						uhrzeit)
				latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))
			else:
				# calculate time to destination
				if set(['abholklient','zielklient','datum','uhrzeit']).intersection(set(form.changed_data)):
					logger.info('calculate time to destination')
					googleDict = DistanceMatrix().getMatrix(
							form.cleaned_data['abholklient'],
							form.cleaned_data['zielklient'],
							datum.datum, 
							uhrzeit)
					latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))	
				else:
					latest_departuretime = datetime.combine(datum.datum, ankunft)
				# calculate time to next client departure place
				timediff = (datetime.combine(datum.datum, instance.uhrzeit) - datetime.combine(datum.datum, ankunft)).total_seconds()
				if timediff < 3600:		# 1h
					logger.info('calculate time to next client departure place')
					googleDict = DistanceMatrix().getMatrix(
							form.cleaned_data['zielklient'],
							instance.abholklient,
							instance.datum.datum, 
							instance.uhrzeit)
					latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))
			return 	latest_departuretime.time()
		return time(0,0,0)

class GuestCount():

	def get(self, form):
		guest_count = int(form.cleaned_data['personenzahl'])
		uhrzeit = form.cleaned_data['uhrzeit']
		datum   = form.cleaned_data['datum']
		bus     = Bus.objects.get(bus=form.cleaned_data['bus'])
		zustieg = form.cleaned_data['zustieg']
		while zustieg:
			instance = Tour.objects.order_by('uhrzeit').filter(bus=bus, datum=datum, uhrzeit__lt=uhrzeit).last()
			if instance:
				guest_count += int(instance.personenzahl)
				zustieg = instance.zustieg
				uhrzeit = str(instance.uhrzeit)
			else:
				return guest_count
		return guest_count

class TourArchive():

	def __init__(self):
		rows = Tour.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		for tag, id in existierende_tage:
			fahrtag = Fahrtag.objects.get(pk=tag)
			if fahrtag.datum < date.today():
				t = get_object_or_404(Tour, pk=id)
				t.archiv=True
				t.save()		
