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

    def get_form_data(self, form_data):
        googleDict = {}
        if settings.USE_GOOGLE:
            if 'entfernung' not in form_data \
                    or form_data.get('entfernung') == '' \
                    or set(['abholklient', 'zielklient', 'datum', 'uhrzeit']).intersection(set(form_data)):
                googleDict = self.getMatrix(
                    form_data.get('abholklient'),
                    form_data.get('zielklient'),
                    form_data.get('datum').datum,
                    form_data.get('uhrzeit'))
        return googleDict

    def getMatrix(self, o, d, startdatum, startzeit):

        origins = ["{} {}, {} {}".format(o.strasse.strasse, o.hausnr, o.ort.plz, o.ort.ort)]
        destinations = ["{} {}, {} {}".format(d.strasse.strasse, d.hausnr, d.ort.plz, d.ort.ort)]
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
            googleDict['arrivaltime'] = time(0, 0, 0)

        return googleDict

# calculate earliest and latest departure times based on previous and next client


class DepartureTime():

    # round given time to next minute
    def time_round_up(self, dt):
        return dt - timedelta(seconds=dt.second) + timedelta(seconds=60) if dt.second > 0 else dt

    # strip seconds from given time
    def time_round_down(self, dt):
        return dt - timedelta(seconds=dt.second)

    # get the nearest tour timeslot start time
    def get_timeslot_start(self, bus, weekday, abholzeit):
        if settings.USE_TOUR_HOURS:
            fahrzeiten = bus.fahrzeiten.filter(tag=weekday).values_list('zeiten', flat=True).first()
            if not fahrzeiten:
                return time(0, 0)
            for fahrzeit in fahrzeiten.split('+'):
                start_end_zeiten = fahrzeit.split('-')
                if abholzeit < datetime.strptime(start_end_zeiten[1], '%H:%M').time():
                    return datetime.strptime(start_end_zeiten[0], '%H:%M').time()
        return time(0, 0)

    # get the nearest tour timeslot end time
    def get_timeslot_end(self, bus, weekday, abholzeit):
        if settings.USE_TOUR_HOURS:
            fahrzeiten = bus.fahrzeiten.filter(tag=weekday).values_list('zeiten', flat=True).first()
            if not fahrzeiten:
                return time(23, 59)
            for fahrzeit in fahrzeiten.split('+'):
                start_end_zeiten = fahrzeit.split('-')
                if abholzeit < datetime.strptime(start_end_zeiten[1], '%H:%M').time():
                    return datetime.strptime(start_end_zeiten[1], '%H:%M').time()
        return time(23, 59)

    # iterate through all previous tours as long as there is a tour join
    # return the instance with the latest arrival time
    def get_latest_arrival_time(self, instance):  # instance is already the next previous tour
        ankunft = instance.ankunft
        return_instance = instance
        while instance.zustieg:
            instance = Tour.objects.order_by('uhrzeit').filter(
                bus=instance.bus.id, datum=instance.datum, uhrzeit__lt=instance.uhrzeit).last()
            if instance.ankunft > ankunft:
                return_instance = instance
        return return_instance

    # calculate whether departure time fits with previous clients tour
    def check_previous_client(self, form_data):
        id = form_data.get('id', 0)
        uhrzeit = form_data.get('uhrzeit')
        datum = form_data.get('datum')
        bus = Bus.objects.get(bus=form_data.get('bus'))

        instance = Tour.objects.order_by('uhrzeit').\
            filter(bus=bus, datum=datum, uhrzeit__lt=uhrzeit).exclude(id__in=[id]).last()
        if instance:
            instance = self.get_latest_arrival_time(instance)
            if form_data.get('zustieg'):
                googleDict = DistanceMatrix().getMatrix(
                    instance.abholklient,
                    form_data.get('abholklient'),
                    instance.datum.datum,
                    instance.uhrzeit)
            else:
                #				logger.info('check driving time from last clients arrival time to this clients start time')
                instance = self.get_latest_arrival_time(instance)
                googleDict = DistanceMatrix().getMatrix(
                    instance.zielklient,
                    form_data.get('abholklient'),
                    instance.datum.datum,
                    instance.ankunft)
            return self.time_round_up(datetime.combine(instance.datum.datum, googleDict['arrivaltime'])).time()
        return time(0, 0, 0)

    # calculate earliest departure time in order to match the start of the tour timeslot
    def check_tour_start(self, form_data):
        id = form_data.get('id', 0)
        uhrzeit = form_data.get('uhrzeit')
        datum = form_data.get('datum')
        bus = Bus.objects.get(bus=form_data.get('bus'))

        if settings.USE_TOUR_HOURS:
            googleDict = DistanceMatrix().getMatrix(
                bus.standort,
                form_data.get('abholklient'),
                datum.datum,
                self.get_timeslot_start(form_data.get('bus'), datum.datum.isoweekday(), uhrzeit))
            return self.time_round_up(datetime.combine(datum.datum, googleDict['arrivaltime'])).time()
        return time(0, 0, 0)

    def check_tour_end(self, form_data):
        uhrzeit = form_data.get('uhrzeit')
        ankunft = form_data.get('ankunft')
        datum = form_data.get('datum')
        bus = Bus.objects.get(bus=form_data.get('bus'))

        # calculate latest departure time in order to match the end of the tour timeslot
        if settings.USE_TOUR_HOURS:
            latest_arrivaltime = self.get_timeslot_end(form_data.get('bus'), datum.datum.isoweekday(), uhrzeit)
            timediff = (datetime.combine(
                datum.datum, latest_arrivaltime) - datetime.combine(datum.datum, uhrzeit)).total_seconds()
            if timediff < 3600:		# 1h
                logger.info('check end of tour is within the tour timeslot')
                googleDict = DistanceMatrix().getMatrix(
                    form_data.get('zielklient'),
                    bus.standort,
                    datum.datum,
                    ankunft)
                if googleDict['arrivaltime'] > latest_arrivaltime:
                    overtime = (datetime.combine(
                        datum.datum, googleDict['arrivaltime']) - datetime.combine(datum.datum, latest_arrivaltime)).total_seconds()
                    latest_departuretime = datetime.combine(datum.datum, uhrzeit) - timedelta(seconds=overtime)
                    return self.time_round_down(latest_departuretime).time()
        return time(23, 59)

    def check_appointment(self, form_data):
        uhrzeit = form_data.get('uhrzeit')
        ankunft = form_data.get('ankunft')
        datum = form_data.get('datum')
        termin = form_data.get('termin')

        # calculate latest departure time for the appointment
        if termin:
            appointment_time = datetime.combine(datetime.combine(datum.datum, uhrzeit), termin)
            arrival_time = datetime.combine(datetime.combine(datum.datum, uhrzeit), ankunft)
            if arrival_time > appointment_time:
                overtime = (arrival_time - appointment_time).total_seconds()
                latest_departuretime = datetime.combine(datum.datum, uhrzeit) - timedelta(seconds=overtime)
                return self.time_round_down(latest_departuretime).time()
        return time(23, 59)

    def check_next_client(self, form_data):
        id = form_data.get('id', 0)
        uhrzeit = form_data.get('uhrzeit')
        ankunft = form_data.get('ankunft')
        datum = form_data.get('datum')
        termin = form_data.get('termin')
        bus = Bus.objects.get(bus=form_data.get('bus'))

        # calculate latest departure time for the next client
        instance = Tour.objects.order_by('uhrzeit').filter(
            bus=bus, datum=datum, uhrzeit__gt=uhrzeit).exclude(id__in=[id]).first()
        if instance:
            #			logger.info('check driving time from this clients arrival to start time of next client')
            latest_departuretime = datetime.combine(instance.datum.datum, instance.uhrzeit)
            if instance.zustieg:
                # calculate time to next departure place
                logger.info('calculate time to next departure place joining in')
                googleDict = DistanceMatrix().getMatrix(
                    form_data.get('abholklient'),
                    instance.abholklient,
                    datum.datum,
                    uhrzeit)
                latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))
            else:
                # calculate time to destination
                #				if set(['abholklient','zielklient','datum','uhrzeit']).intersection(set(form.changed_data)):
                logger.info('calculate time to destination')
                googleDict = DistanceMatrix().getMatrix(
                    form_data.get('abholklient'),
                    form_data.get('zielklient'),
                    datum.datum,
                    uhrzeit)
                latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))
#				else:
#					latest_departuretime = datetime.combine(datum.datum, ankunft)
                # calculate time to next client departure place
                timediff = (datetime.combine(
                    datum.datum, instance.uhrzeit) - datetime.combine(datum.datum, ankunft)).total_seconds()
                if timediff < 3600:		# 1h
                    logger.info('calculate time to next client departure place')
                    googleDict = DistanceMatrix().getMatrix(
                        form_data.get('zielklient'),
                        instance.abholklient,
                        instance.datum.datum,
                        instance.uhrzeit)
                    latest_departuretime = (latest_departuretime - timedelta(seconds=googleDict['duration_value']))
            return self.time_round_up(latest_departuretime).time()
        return time(23, 59)


class GuestCount():

    def get(self, form_data):
        guest_count = int(form_data.get('personenzahl'))
        uhrzeit = form_data.get('uhrzeit')
        datum = form_data.get('datum')
        bus = Bus.objects.get(bus=form_data.get('bus'))
        zustieg = form_data.get('zustieg')
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
        rows = Tour.objects.filter(archiv=False).values_list('datum', 'id')
        existierende_tage = [row for row in rows]
        for tag, id in existierende_tage:
            fahrtag = Fahrtag.objects.get(pk=tag)
            if fahrtag.datum < date.today():
                t = get_object_or_404(Tour, pk=id)
                t.archiv = True
                t.save()
