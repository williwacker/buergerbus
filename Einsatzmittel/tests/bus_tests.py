from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.test import TestCase

from Einsatzmittel.models import Bus, Wochentage


class BusTestCase(TestCase):
    def setUp(self):
        if Wochentage.objects.count() == 0:
            call_command('loaddata', 'wochentage.json', app_label='Einsatzmittel', verbosity=0)
        wt1 = Wochentage.objects.get(name='Montag')
        wt2 = Wochentage.objects.get(name='Dienstag')
        wt3 = Wochentage.objects.get(name='Mittwoch')
        wt4 = Wochentage.objects.get(name='Donnerstag')
        wt5 = Wochentage.objects.get(name='Freitag')

        if Bus.objects.count() == 0:
            bus1 = Bus.objects.create(bus='Bus 1', sitzplaetze=8, plantage=settings.COUNT_TOUR_DAYS)
            bus1.fahrtage.add(wt2, wt4)
            bus2 = Bus.objects.create(bus='Bus 2', sitzplaetze=8, email='dummy@dummy.de', plantage=20)
            bus2.fahrtage.add(wt3,wt5)

    def test_bus(self):
        """Bus model tests"""
        bus1 = Bus.objects.get(bus="Bus 1")
        bus2 = Bus.objects.get(bus="Bus 2")
        self.assertEqual(bus2._permission_codename(), 'Bus_{}_editieren'.format(bus2.id))
        self.assertEqual(bus2._permission_name(), 'Bus 2 verwalten')
        permission = Permission.objects.get(name=bus1._permission_name())
        self.assertEqual(permission.codename, bus1._permission_codename())
        wt1 = Wochentage.objects.get(name='Montag')
        self.assertEqual(wt1.id, 1)
