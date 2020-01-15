import csv
import datetime
import io
import logging
import os
import time
from os import environ, getcwd

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.mail import EmailMessage, get_connection
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404

### Fahrtage und Bürotage schreiben
from Basis.berechnung_feiertage import Holidays
from Einsatzmittel.models import Buero, Bus
from Einsatztage.models import Buerotag, Fahrtag
from Tour.models import Tour

from .models import Fahrtag

logger = logging.getLogger(__name__)


def get_holidays():
	# die nächsten Feiertage ausrechnen
	holiday_list = []
	holidays = Holidays(int(time.strftime("%Y")), 'RP')
	for holiday in holidays.get_holiday_list():
		holiday_list.append(holiday[0])
	holidays = Holidays(int(time.strftime("%Y"))+1, 'RP')
	for holiday in holidays.get_holiday_list():
		holiday_list.append(holiday[0])
	return holiday_list

class FahrtageSchreiben():

	def __init__(self):
		self.write_new_fahrtage()
		self.archive_past_fahrtage()

	def write_new_fahrtage(self,changedate=None):
		# die nächsten Feiertage ausrechnen
		holiday_list = get_holidays()

		rows = Bus.objects.order_by('bus').values_list('id','fahrtage')
		array = [row for row in rows]
		for item in array:
			id, fahrtag = item
			bus = get_object_or_404(Bus, pk=id)
			rows = Fahrtag.objects.filter(team=bus, archiv=False).values_list('datum',flat=True)
			existierende_tage = [row for row in rows]

			# die Fahrtage für die nächsten n Tage ausrechnen
			max_days = max(settings.COUNT_DRIVING_DAYS, bus.plantage, settings.COUNT_TOUR_DAYS)
			for i in range(1,max_days):
				neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
				if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
					if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
						if neuer_tag.isoweekday() == fahrtag:   # Tag ist ein Fahrtag
							if changedate != neuer_tag:
								t = Fahrtag(datum=neuer_tag, team=bus)
								t.save()

	def archive_past_fahrtage(self):
		rows = Fahrtag.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		if existierende_tage:
			for tag, id in existierende_tage:
				if tag < datetime.date.today():
					t = get_object_or_404(Fahrtag, pk=id)
					t.archiv=True
					t.save()

class BuerotageSchreiben():

	def __init__(self):
		self.write_new_buerotage()
		self.archive_past_buerotage()

	def write_new_buerotage(self,changedate=None):
		# die nächsten Feiertage ausrechnen
		holiday_list = get_holidays()
		
		rows = Buero.objects.order_by('buero').values_list('id','buerotage')
		array = [row for row in rows]
		for item in array:
			id, buerotag = item
			b = get_object_or_404(Buero, pk=id)
			rows = Buerotag.objects.filter(team=b, archiv=False).values_list('datum',flat=True)
			existierende_tage = [row for row in rows]

			# die Bürotage für die nächsten n Tage ausrechnen
			max_days = settings.COUNT_OFFICE_DAYS
			for i in range(1,max_days):
				neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
				if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
					if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
						if neuer_tag.isoweekday() == buerotag:   # Tag ist ein Bürotag
							if changedate != neuer_tag:
								t = Buerotag(datum=neuer_tag, team=b)
								t.save()

	def archive_past_buerotage(self):
		rows = Buerotag.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		if existierende_tage:
			for tag, id in existierende_tage:
				if tag < datetime.date.today():
					t = get_object_or_404(Buerotag, pk=id)
					t.archiv=True
					t.save()

# write fahrplan to csv file for backup purposes

class FahrplanBackup():
	
	def __init__(self):
		self.send_backup()

	def send_backup(self):
		mail_backend = get_connection()
		bus_list = list(Bus.objects.values_list('id','bus','email'))
		for [bus_id, bus, email] in bus_list:
			filelist = []
			id_list = list(Tour.objects.filter(archiv=False, bus_id=bus_id).values_list('datum', flat=True).distinct())
			for id in id_list:
				filelist += self.export_as_csv(id)
			if not email or not filelist:
				continue
			mail_text = 'Liebe Koordinatoren,\nAnbei die bisherigen Fahrpläne. Diese sind nur zu verwenden im Fall daß der Web-Server des Bürgerbus Portals ausfällt.' 
			message = EmailMessage(
						from_email=settings.EMAIL_HOST_USER,
						to=[email,],
						connection=mail_backend,
						subject="Fahrplan Backup {} vom {}".format(bus, datetime.date.today()), 
						body=mail_text,
					)
			attachments = []  # start with an empty list
			for filename in filelist:
				# create the attachment triple for this filename
				content = open(filename, 'rb').read()
				import os
				attachment = (os.path.basename(filename), content, 'application/csv')
				# add the attachment to the list
				attachments.append(attachment)
			message.attachments = attachments
			message.send()

	def export_as_csv(self, id):
		fahrtag   = get_object_or_404(Fahrtag, pk=id)
		tour_list = Tour.objects.order_by('uhrzeit').filter(datum=id)
		filename = 'Buergerbus_Fahrplan_{}_{}.csv'.format(str(fahrtag.team).replace(' ','_'), fahrtag.datum)
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=filename'
		filepath = settings.TOUR_PATH + filename
		writer = csv.writer(response)
		writer.writerow(['sep=,'])
		writer.writerow(['','Fahrer Vormittag',fahrtag.fahrer_vormittag])
		writer.writerow(['','Fahrer Nachmittag',fahrtag.fahrer_nachmittag])
		writer.writerow([''])
		writer.writerow(['Uhrzeit', 'Fahrgast', 'Telefon', 'Zustieg', 'Anzahl', 'Abholort', 'Zielort', 'Entfernung', 'Ankunft', 'Bemerkung'])

		for tour in tour_list:
			list = []
			list.append(tour.uhrzeit.strftime("%H:%M"))
			list.append(tour.klient.name)
			list.append('' if not tour.klient.telefon else tour.klient.telefon + '' if not tour.klient.mobil else tour.klient.mobil)
			list.append('N' if not tour.zustieg else 'J')
			list.append(str(tour.personenzahl))
			list.append(tour.abholort.replace('\n',' '))
			list.append(tour.zielort.replace('\n',' '))
			list.append(tour.entfernung)
			list.append(tour.ankunft.strftime("%H:%M") if tour.ankunft else '')
			list.append(tour.bemerkung + tour.klient.bemerkung)
			writer.writerow(list)
		try:
			with open(filepath, 'wb') as f:
				f.write(response.content)
			with io.open(filepath, mode="r", encoding="utf8") as fd:
				content = fd.read()
			with io.open(filepath, mode="w", encoding="cp1252") as fd:
				fd.write(content)		
		except:
			logger.info("{}: document={} could not be written".format(__name__, filepath))
		return [filepath]					
