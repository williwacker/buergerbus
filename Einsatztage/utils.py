import datetime, time
from os import environ,getcwd
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import Permission
from django.conf import settings
from .models import Fahrtag
from Einsatzmittel.models import Bus, Buero
from Basis.utils import has_perm

### Fahrtage und Bürotage schreiben
from Basis.berechnung_feiertage import Holidays
from Einsatztage.models import Fahrtag, Buerotag

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

	def __init__(self, user):
		os_user = (lambda: environ["USERNAME"] if "D:" in getcwd() else environ["USER"])()
		if os_user in ('Werner','root') or has_perm(user, 'Einsatztage.change_fahrtage'):
			self.write_new_fahrtage()
			self.archive_past_fahrtage()

	def write_new_fahrtage(self,changedate=None):
		# die nächsten Feiertage ausrechnen
		holiday_list = get_holidays()

		rows = Bus.objects.order_by('bus').values_list('id','fahrtage')
		array = [row for row in rows]
		for item in array:
			id, fahrtag = item
			b = Bus.objects.get(pk=id)
			rows = Fahrtag.objects.filter(team=b, archiv=False).values_list('datum',flat=True)
			existierende_tage = [row for row in rows]

			# die Fahrtage für die nächsten n Tage ausrechnen
			max_days = settings.COUNT_DRIVING_DAYS
			for i in range(1,max_days):
				neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
				if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
					if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
						if neuer_tag.isoweekday() == fahrtag:   # Tag ist ein Fahrtag
							if changedate != neuer_tag:
								t = Fahrtag(datum=neuer_tag, team=b)
								t.save()

	def archive_past_fahrtage(self):
		rows = Fahrtag.objects.filter(archiv=False).values_list('datum','id')
		existierende_tage = [row for row in rows]
		if existierende_tage:
			for tag, id in existierende_tage:
				if tag < datetime.date.today():
					t = Fahrtag.objects.get(pk=id)
					t.archiv=True
					t.save()

class BuerotageSchreiben():

	def __init__(self,user):
		os_user = (lambda: environ["USERNAME"] if "D:" in getcwd() else environ["USER"])()
		if os_user in ('Werner','root') or has_perm(user, 'Einsatztage.change_buerotage'):
			self.write_new_buerotage()
			self.archive_past_buerotage()

	def write_new_buerotage(self,changedate=None):
		# die nächsten Feiertage ausrechnen
		holiday_list = get_holidays()

		rows = Buero.objects.order_by('buero').values_list('id','buerotage')
		array = [row for row in rows]
		for item in array:
			id, buerotag = item
			b = Buero.objects.get(pk=id)
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
					t = Buerotag.objects.get(pk=id)
					t.archiv=True
					t.save()