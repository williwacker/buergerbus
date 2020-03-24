from contextlib import contextmanager
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.test import TestCase

from Basis.telefonbuch_suche import Telefonbuch
from Einsatzmittel.models import Bus
from Einsatzmittel.tests import BusTestCase
from Klienten.models import Klienten, Orte, Strassen


class DienstleisterTestCase(TestCase):
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
            s2 = Strassen.objects.create(strasse='Sackgassse', ort=o1)
            Strassen.objects.create(strasse='Hauptstrasse', ort=o2)
            Strassen.objects.create(strasse='Sackgassse', ort=o2)
            Strassen.objects.create(strasse='Hauptstrasse', ort=o3)
            Strassen.objects.create(strasse='Sackgassse', ort=o3)
            Strassen.objects.create(strasse='Hauptstrasse', ort=o4)
            Strassen.objects.create(strasse='Sackgassse', ort=o4)
            Strassen.objects.create(strasse='Hauptstrasse', ort=o5)
            Strassen.objects.create(strasse='Sackgassse', ort=o5)

    def test_dienstleister_google(self):
        """dienstleister model tests with use_google=True"""
        setattr(settings, 'USE_GOOGLE', True)
        o1 = Orte.objects.get(ort='Alzey', plz=55232)
        s1 = Strassen.objects.get(strasse='Hauptstrasse', ort=o1)
        d1 = Klienten.objects.create(name='Dr. Mabuse', telefon='06731-1111',
                                     mobil='0150-1111', ort=o1, strasse=s1, hausnr='25', typ='D')
        self.assertEqual(str(d1.latitude)[:5], '49.73')
        self.assertEqual(str(d1.longitude)[:4], '8.06')
        self.assertEqual(d1.dsgvo, '99')
        self.assertEqual(d1.bus, None)

    def test_dienstleister_non_google(self):
        """dienstleister model tests with use_google=False"""
        setattr(settings, 'USE_GOOGLE', False)
        o1 = Orte.objects.get(ort='Alzey', plz=55232)
        s2 = Strassen.objects.get(strasse='Sackgassse', ort=o1)
        d2 = Klienten.objects.create(name='Löwen Apotheke', telefon='06731-222',
                                     mobil='', ort=o1, strasse=s2, hausnr='1', typ='D')
        self.assertAlmostEqual(d2.latitude, Decimal(0))
        self.assertAlmostEqual(d2.longitude, Decimal(0))
        self.assertEqual(d2.dsgvo, '99')
        self.assertEqual(d2.bus, None)

    def test_dienstleister_search_dastelefonbuch(self):
        """dienstleister model tests with search via dastelefonbuch"""
        suchname = 'Becker'
        suchort = 'Alzey'
        result_list = Telefonbuch().dastelefonbuch(suchname, suchort, 'D')
        self.assertIsNotNone(result_list)
        self.assertGreater(len(result_list), 0)
        for result in result_list:
            self.assertTrue({'na', 'ci', 'pc', 'ph', 'mph', 'hn'} <= set(result))

    def test_dienstleister_search_dasoertliche(self):
        """dienstleister model tests with search via dasoertliche"""
        suchname = 'Becker'
        suchort = 'Alzey'
        result_list = Telefonbuch().dasoertliche(suchname, suchort, 'D')
        self.assertIsNotNone(result_list)
        self.assertGreater(len(result_list), 0)
        for result in result_list:
            self.assertTrue({'na', 'ci', 'pc', 'ph', 'mph', 'hn'} <= set(result))
