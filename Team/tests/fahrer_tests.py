from django.conf import settings
from django.test import TestCase

from Einsatzmittel.models import Bus
from Basis.tests import UserTestCase
from Einsatzmittel.tests import BusTestCase
from Team.models import Fahrer
from django.contrib.auth.models import User


class FahrerTestCase(TestCase):
	def setUp(self):
		BusTestCase().setUp()
		UserTestCase().setUp()
		UserTestCase().test_user()

		bus1 = Bus.objects.get(bus='Bus 1')
		bus2 = Bus.objects.get(bus='Bus 2')
		user = User.objects.get(username='testuser')
		if Fahrer.objects.count() == 0:
			Fahrer.objects.create(benutzer=user, team=bus1, aktiv=False)
			Fahrer.objects.create(benutzer=user, team=bus2)

	def test_fahrer(self):
		"""Fahrer model tests"""
		bus1 = Bus.objects.get(bus='Bus 1')
		bus2 = Bus.objects.get(bus='Bus 2')
		user = User.objects.get(username='testuser')
		f1 = Fahrer.objects.get(benutzer=user, team=bus1)
		f2 = Fahrer.objects.get(benutzer=user, team=bus2)
		self.assertEqual(f1.aktiv, False)
		self.assertEqual(f2.aktiv, True)
		self.assertEqual(f1.team.bus, bus1.bus)
