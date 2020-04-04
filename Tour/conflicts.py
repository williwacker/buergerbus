from datetime import datetime, time, timedelta

from django.utils.encoding import force_text

from Basis.utils import append_br
from Tour.models import Tour
from Tour.utils import DepartureTime, DistanceMatrix


class Conflicts():
	def __init__(self, instance, use_conflict_time):
		if instance:
			self.instance = instance
			self.previous_instance = DepartureTime().get_previous_client_by_instance(instance)
			self.next_instance = DepartureTime().get_next_client_by_instance(instance)
			if use_conflict_time and self.instance.konflikt_zeiten != '':
				self.instance.uhrzeit = datetime.strptime(
					self.instance.konflikt_zeiten[2:7], '%H:%M').time()
			self.instance.konflikt = ''
			self.instance.konflikt_richtung = ''
			self.instance.konflikt_zeiten = ''
			self.form_data = self.instance.__dict__
			self.form_data.update([
				('datum', self.instance.datum),
				('bus', self.instance.bus),
				('abholklient', self.instance.abholklient),
				('zielklient', self.instance.zielklient)
			])

			self.perform_checks()

	def perform_checks(self):
		self.check_unique_time()
		self.get_google_data()
		self.check_earliest_departuretime()
		self.check_latest_departuretime()
		return self.instance

	def update_conflict_direction(self, direction):
		if len(self.instance.konflikt_richtung) == 0:
			self.instance.konflikt_richtung = direction
		else:
			if self.instance.konflikt_richtung != 'B' and self.instance.konflikt_richtung != direction:
				self.instance.konflikt_richtung = 'B'

	def check_unique_time(self):
		# prüfe auf unique Tour Abfahrtszeit. Bei Zustieg addiere solange 1 sec bis die Uhrzeit unique ist
		uhrzeit = self.instance.uhrzeit
		dependent_instance = Tour.objects.filter(
			bus=self.instance.bus, datum=self.instance.datum, uhrzeit=self.instance.uhrzeit).exclude(
			id__in=[self.instance.id]).first()
		while dependent_instance:
			uhrzeit = (datetime.combine(datetime(year=100, month=1, day=1),
										dependent_instance.uhrzeit) + timedelta(seconds=1)).time()
			dependent_instance = Tour.objects.filter(
				bus=self.instance.bus, datum=self.instance.datum, uhrzeit=uhrzeit).exclude(
				id__in=[self.instance.id]).first()
		self.instance.uhrzeit = uhrzeit

	def get_google_data(self):
		# errechne die Distanz und Ankunftszeit
		googleDict = DistanceMatrix().get_form_data(self.form_data)
		if googleDict:
			self.instance.entfernung = googleDict['distance']
			self.form_data['entfernung'] = googleDict['distance']
			self.instance.ankunft = googleDict['arrivaltime']
			self.form_data['ankunft'] = googleDict['arrivaltime']
			self.form_data['duration_value'] = googleDict['duration_value']

	def check_earliest_departuretime(self):
		earliest_departure_conflict = False

		# Kann der Fahrer pünktlich am Morgen oder aus der Pause starten?
		frueheste_abfahrt_1 = DepartureTime().check_tour_start(self.form_data)
		if frueheste_abfahrt_1 > self.instance.uhrzeit:
			tourstart = DepartureTime().get_timeslot_start(
				self.instance.bus,
				self.instance.datum.datum.isoweekday(),
				self.instance.uhrzeit)
			earliest_departure_conflict = True
			self.update_conflict_direction('U')
			self.instance.konflikt = append_br(
				self.instance.konflikt,
				"Tour Start um {} kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(
					tourstart.strftime("%H:%M"),
					frueheste_abfahrt_1.strftime("%H:%M")))

		# Kann der Bus zum gewünschten Zeitpunkt am Abholort sein ?
		frueheste_abfahrt_2 = DepartureTime().check_previous_client(self.form_data, self.previous_instance)
		if frueheste_abfahrt_2 == time(0, 0, 0):
			self.instance.zustieg = False

		if frueheste_abfahrt_2 > self.instance.uhrzeit:
			earliest_departure_conflict = True
			self.update_conflict_direction('U')
			self.instance.konflikt = append_br(
				self.instance.konflikt,
				"Abfahrtszeit kann aufgrund der vorhergehenden Tour nicht eingehalten werden. Frühest mögliche Abfahrt um {}".
				format(frueheste_abfahrt_2.strftime("%H:%M")))

		if earliest_departure_conflict:
			self.instance.konflikt_zeiten += force_text('\n↑', encoding='utf-8', strings_only=False, errors='strict') + \
				max(frueheste_abfahrt_1, frueheste_abfahrt_2).strftime("%H:%M")

	def check_latest_departuretime(self):
		latest_departure_conflict = False

		# Kann der Fahrer pünktlich Pause oder Feierabend machen?
		spaeteste_abfahrt_1 = DepartureTime().check_tour_end(self.form_data)
		if spaeteste_abfahrt_1 < self.instance.uhrzeit:
			tourende = Latest_DepartureTime().get_timeslot_end(
				self.instance.bus,
				self.instance.datum.datum.isoweekday(),
				self.instance.uhrzeit)
			latest_departure_conflict = True
			self.update_conflict_direction('D')
			self.instance.konflikt = append_br(
				self.instance.konflikt,
				"Tour Ende um {} kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(
					tourende.strftime("%H:%M"),
					spaeteste_abfahrt_1.strftime("%H:%M")))

		# Kann der Termin eingehalten werden?
		spaeteste_abfahrt_2 = DepartureTime().check_appointment(self.form_data)
		if spaeteste_abfahrt_2 < self.instance.uhrzeit:
			latest_departure_conflict = True
			self.update_conflict_direction('D')
			self.instance.konflikt = append_br(
				self.instance.konflikt,
				"Termin um {} kann nicht eingehalten werden. Empfohlene Abfahrt vor {}".format(
					self.instance.termin.strftime("%H:%M"),
					spaeteste_abfahrt_2.strftime("%H:%M")))

		# Kann der nächste Fahrgast zum geplanten Zeitpunkt abgeholt werden?
		spaeteste_abfahrt_3 = DepartureTime().check_next_client(self.form_data, self.next_instance)
		# Konflikt nur anzeigen falls Abfahrt noch früher erfolgen müsste
		if spaeteste_abfahrt_3 < self.instance.uhrzeit and spaeteste_abfahrt_3 < spaeteste_abfahrt_2:
			latest_departure_conflict = True
			self.update_conflict_direction('D')
			self.instance.konflikt = append_br(
				self.instance.konflikt,
				"Abfahrtszeit des nächsten Fahrgastes kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(
					spaeteste_abfahrt_3.strftime("%H:%M")))

		if latest_departure_conflict:
			self.instance.konflikt_zeiten += force_text('\n↓', encoding='utf-8', strings_only=False, errors='strict') + \
				min(spaeteste_abfahrt_1, spaeteste_abfahrt_2, spaeteste_abfahrt_3).strftime("%H:%M")
