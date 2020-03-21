from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.test import TestCase

from Einsatzmittel.models import Bus, Wochentage, Fahrzeiten


class BusTestCase(TestCase):
    def setUp(self):
        if Wochentage.objects.count() == 0:
            call_command('loaddata', 'wochentage.json', app_label='Einsatzmittel', verbosity=0)
        if Fahrzeiten.objects.count() == 0:
            call_command('loaddata', 'fahrzeiten.json', app_label='Einsatzmittel', verbosity=0)            
        fz1 = Fahrzeiten.objects.get(id=1)
        fz2 = Fahrzeiten.objects.get(id=2)
        fz3 = Fahrzeiten.objects.get(id=3)
        fz4 = Fahrzeiten.objects.get(id=4)
        fz5 = Fahrzeiten.objects.get(id=5)

        if Bus.objects.count() == 0:
            bus1 = Bus.objects.create(bus='Bus 1', sitzplaetze=8, plantage=settings.COUNT_TOUR_DAYS)
            bus1.fahrzeiten.add(fz1, fz3)
            bus2 = Bus.objects.create(bus='Bus 2', sitzplaetze=8, email='dummy@dummy.de', plantage=20)
            bus2.fahrzeiten.add(fz2,fz4)

    def test_bus(self):
        """Bus model tests"""
        bus1 = Bus.objects.get(bus="Bus 1")
        bus2 = Bus.objects.get(bus="Bus 2")
        self.assertEqual(bus2._permission_codename(), 'Bus_{}_editieren'.format(bus2.id))
        self.assertEqual(bus2._permission_name(), 'Bus 2 verwalten')
        permission = Permission.objects.get(name=bus1._permission_name())
        self.assertEqual(permission.codename, bus1._permission_codename())
