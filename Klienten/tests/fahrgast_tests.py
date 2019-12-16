from contextlib import contextmanager
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from Einsatzmittel.models import Bus
from Einsatzmittel.tests import BusTestCase
from Klienten.models import Klienten, Orte, Strassen


class FahrgastTestCase(TestCase):
	def setUp(self):
		BusTestCase().setUp()
		bus1 = Bus.objects.get(bus='Bus 1')
		bus2 = Bus.objects.get(bus='Bus 2')
		if Orte.objects.count() == 0:
			o1 = Orte.objects.create(ort='Alzey', plz=55232)
			o2 = Orte.objects.create(ort='Eppelsheim', plz=55234, bus=bus1)
			o3 = Orte.objects.create(ort='Kettenheim', plz=55234, bus=bus1)
			o4 = Orte.objects.create(ort='Ober-Flörsheim', plz=55234, bus=bus1)
			o5 = Orte.objects.create(ort='Albig', plz=55234, bus=bus2)
		if Strassen.objects.count() == 0:
			s1 = Strassen.objects.create(strasse='Hauptstrasse', ort=o1)
			s2 = Strassen.objects.create(strasse='Sackgasse', ort=o1)
			Strassen.objects.create(strasse='Hauptstrasse', ort=o2)
			Strassen.objects.create(strasse='Sackgasse', ort=o2)
			Strassen.objects.create(strasse='Hauptstrasse', ort=o3)
			Strassen.objects.create(strasse='Sackgasse', ort=o3)
			Strassen.objects.create(strasse='Hauptstrasse', ort=o4)
			Strassen.objects.create(strasse='Sackgasse', ort=o4)
			Strassen.objects.create(strasse='Hauptstrasse', ort=o5)
			Strassen.objects.create(strasse='Sackgasse', ort=o5)

	def test_fahrgast_outside(self):
		"""fahrgast model tests with ALLOW_OUTSIDE_CLIENTS=True"""
		setattr(settings, 'ALLOW_OUTSIDE_CLIENTS', True)
		setattr(settings, 'USE_GOOGLE', True)
		o1 = Orte.objects.get(ort='Alzey')
		s1 = Strassen.objects.get(strasse='Hauptstrasse', ort=o1)
		try: d1 = Klienten.objects.create(name='Becker, Willi', telefon='06731-1111', mobil='0150-1111', ort=o1, strasse=s1, hausnr='25', typ='F')
		except: pass
		self.assertEqual(str(d1.latitude)[:5], '49.73')
		self.assertEqual(str(d1.longitude)[:4], '8.06')
		self.assertEqual(d1.dsgvo, '01')
		self.assertEqual(d1.bus, None)

	def test_fahrgast_non_outside_fail(self):
		"""fahrgast model tests with ALLOW_OUTSIDE_CLIENTS=False and Client create exception"""
		setattr(settings, 'ALLOW_OUTSIDE_CLIENTS', False)
		o1 = Orte.objects.get(ort='Alzey')
		s2 = Strassen.objects.get(strasse='Sackgasse', ort=o1)
		with self.assertRaises(ValidationError) as cm:
			d2 = Klienten.objects.create(name='Schmitt, Horst', telefon='06731-222', mobil='', ort=o1, strasse=s2, hausnr='1', typ='F')
		self.assertEqual(str(cm.exception.messages), "['Fahrgäste aus diesem Ort sind nicht erlaubt']")

	def test_fahrgast_non_outside_success(self):
		"""fahrgast model tests with ALLOW_OUTSIDE_CLIENTS=False"""
		setattr(settings, 'ALLOW_OUTSIDE_CLIENTS', False)
		o2 = Orte.objects.get(ort='Eppelsheim')
		s2 = Strassen.objects.get(strasse='Sackgasse', ort=o2)
		try:d2 = Klienten.objects.create(name='Schmitt, Horst', telefon='06731-222', mobil='', ort=o2, strasse=s2, hausnr='1', typ='F')
		except: pass
		self.assertEqual(d2.dsgvo, '01')
		self.assertEqual(d2.bus.bus, 'Bus 1')
