import datetime, time
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import Permission
from django.conf import settings
from .models import Fahrtag
from Einsatzmittel.models import Bus, Buero


### Fahrtage und Bürotage schreiben
from Basis.berechnung_feiertage import Holidays
from Einsatztage.models import Fahrtag, Buerotag

wochentage = ['Mo','Di','Mi','Do','Fr','Sa','So']

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

	def read_bus_tage(self):
		bus_dict = {}
		rows = Bus.objects.order_by('bus').values_list('bus','fahrtage')
		array = [row for row in rows]
		for item in array:
			bus, fahrtage = item
			tage_nr = []
			tage = fahrtage.split(",")
			for tag in tage:
				tage_nr.append(wochentage.index(tag))
			bus_dict[bus] = tage_nr
		return(bus_dict)

	def write_new_fahrtage(self,changedate=None):
		# die nächsten Feiertage ausrechnen
		holiday_list = get_holidays()

		bus_tage = self.read_bus_tage()
		for bus_id in bus_tage:
			b = Bus.objects.get(pk=int(bus_id))
			rows = Fahrtag.objects.filter(team=b, archiv=False).values_list('datum',flat=True)
			existierende_tage = [row for row in rows]

			# die Fahrtage für die nächsten n Tage ausrechnen
			max_days = settings.COUNT_DRIVING_DAYS
			for i in range(1,max_days):
				neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
				if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
					if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
						if neuer_tag.weekday() in bus_tage[bus_id]:   # Tag ist ein Fahrtag
							if changedate != neuer_tag:
								t = Fahrtag(datum=neuer_tag, team=b)
								t.save()

	def archive_past_fahrtage(self):
		rows = Fahrtag.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		for tag, id in existierende_tage:
			if tag < datetime.date.today():
				t = Fahrtag.objects.get(pk=id)
				t.archiv=True
				t.save()

class BuerotageSchreiben():

	def read_buero_tage(self):
		buero_dict = {}
		rows = Buero.objects.order_by('id').values_list('id','buerotage')
		array = [row for row in rows]
		for item in array:
			buero, buerotage = item
			tage_nr = []
			tage = buerotage.split(",")
			for tag in tage:
				tage_nr.append(wochentage.index(tag))
			buero_dict[buero] = tage_nr
		return(buero_dict)

	def write_new_buerotage(self,changedate):
		# die nächsten Feiertage ausrechnen
		holiday_list = get_holidays()

		buero_tage = self.read_buero_tage()
		for id in buero_tage:
			b = Buero.objects.get(pk=id)
			rows = Buerotag.objects.filter(team=b, archiv=False).values_list('datum',flat=True)
			existierende_tage = [row for row in rows]

			# die Bürotage für die nächsten n Tage ausrechnen
			max_days = settings.COUNT_OFFICE_DAYS
			for i in range(1,max_days):
				neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
				if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
					if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
						if neuer_tag.weekday() in buero_tage[id]:   # Tag ist ein Bürotag
							if changedate != neuer_tag:
								t = Buerotag(datum=neuer_tag, team=b)
								t.save()

	def archive_past_buerotage(self):
		rows = Buerotag.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		for tag, id in existierende_tage:
			if tag < datetime.date.today():
				t = Buerotag.objects.get(pk=id)
				t.archiv=True
				t.save()