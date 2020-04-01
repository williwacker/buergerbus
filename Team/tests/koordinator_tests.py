from django.conf import settings
from django.test import TestCase

from Einsatzmittel.models import Bus
from Basis.tests import UserTestCase
from Einsatzmittel.tests import BueroTestCase
from Team.models import Koordinator
from django.contrib.auth.models import User


class KoordinatorTestCase(TestCase):
	def setUp(self):
		BueroTestCase().setUp()
		UserTestCase().setUp()
		UserTestCase().test_user()

		buero1 = Buero.objects.get(buero='Büro 1')
		buero2 = Buero.objects.get(buero='Büro 2')
		user = User.objects.get(username='testuser')
		if Koordinator.objects.count() == 0:
			Koordinator.objects.create(benutzer=user, team=buero1, aktiv=False)
			Koordinator.objects.create(benutzer=user, team=buero2)

	def test_koordinator(self):
		"""Koordinator model tests"""
		buero1 = Buero.objects.get(buero='Büro 1')
		buero2 = Buero.objects.get(buero='Büro 2')
		user = User.objects.get(username='testuser')
		k1 = Koordinator.objects.get(benutzer=user, team=buero1)
		k2 = Koordinator.objects.get(benutzer=user, team=buero2)
		self.assertEqual(f1.aktiv, False)
		self.assertEqual(f2.aktiv, True)
		self.assertEqual(f1.team.buero, buero1.buero)
