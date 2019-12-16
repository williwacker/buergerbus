from django.conf import settings
from django.test import TestCase

from Einsatzmittel.models import Buero, Wochentage
from Einsatzmittel.tests import BueroTestCase
from Einsatztage.models import Buerotag
from Einsatztage.utils import BuerotageSchreiben


class BuerotagTestCase(TestCase):
    def setUp(self):
        BueroTestCase().setUp()

    def test_buerotag_no_office_days(self):
        """Buerotag model tests with count days=0"""
        setattr(settings, 'COUNT_OFFICE_DAYS', 0)
        BuerotageSchreiben().write_new_buerotage()
        buero1 = Buero.objects.first()
        bt_count = Buerotag.objects.filter(team=buero1, archiv=False).count()
        self.assertEqual(bt_count, 0)

    def test_Buerotag_with_driving_days(self):
        """Buerotag model tests with count days>0"""
        setattr(settings, 'COUNT_OFFICE_DAYS', 20)
        BuerotageSchreiben().write_new_buerotage()

        buero1 = Buero.objects.first()
        buero2 = Buero.objects.last()

        bt_buero1_count = Buerotag.objects.filter(team=buero1).count()
        bt_buero2_count = Buerotag.objects.filter(team=buero2).count()
        self.assertGreater(bt_buero1_count, 0)
        self.assertGreater(bt_buero2_count, 0)

        bt_buero1 = Buerotag.objects.filter(team=buero1).first()
        bt_buero2 = Buerotag.objects.filter(team=buero2).first()
        self.assertEqual(bt_buero1.wochentag in ['Mo','Di'], True)
        self.assertEqual(bt_buero2.wochentag in ['Mi','Do'], True)
