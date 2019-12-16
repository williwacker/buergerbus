from django.conf import settings
from django.test import TestCase

from Einsatzmittel.models import Bus
from Einsatzmittel.tests import BusTestCase
from Team.models import Fahrer


class FahrerTestCase(TestCase):
	def setUp(self):
		BusTestCase().setUp()
		bus1 = Bus.objects.get(bus='Bus 1')
		bus2 = Bus.objects.get(bus='Bus 2')
		if Fahrer.objects.count() == 0:
			Fahrer.objects.create(name='Fahrer1, Gerd', email='email1@email.com', telefon='01234-678', mobil='0111-345', team=bus1, aktiv=False)
			Fahrer.objects.create(name='Fahrer2, Bernd', email='email2@email.com', team=bus1)
			Fahrer.objects.create(name='Fahrer1, Gerd', email='email1@email.com', team=bus2)

	def test_fahrer(self):
		"""Fahrer model tests"""
		bus1 = Bus.objects.get(bus='Bus 1')
		bus2 = Bus.objects.get(bus='Bus 2')
		f1 = Fahrer.objects.get(name='Fahrer1, Gerd', team=bus1)
		f2 = Fahrer.objects.get(name='Fahrer2, Bernd', team=bus1)
		f3 = Fahrer.objects.get(name='Fahrer1, Gerd', team=bus2)
		self.assertEqual(f1.aktiv, False)
		self.assertEqual(f2.aktiv, True)
		self.assertEqual(f3.aktiv, True)
		self.assertEqual(f1.team.bus, bus1.bus)
