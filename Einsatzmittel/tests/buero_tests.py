from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.test import TestCase

from Einsatzmittel.models import Buero, Wochentage


class BueroTestCase(TestCase):
    def setUp(self):
        if Wochentage.objects.count() == 0:
            call_command('loaddata', 'wochentage.json', app_label='Einsatzmittel', verbosity=0)
        wt1 = Wochentage.objects.get(name='Montag')
        wt2 = Wochentage.objects.get(name='Dienstag')
        wt3 = Wochentage.objects.get(name='Mittwoch')
        wt4 = Wochentage.objects.get(name='Donnerstag')

        buero1 = Buero.objects.create(buero='Büro 1')
        buero1.buerotage.add(wt1, wt2)
        buero2 = Buero.objects.create(buero='Büro 2')
        buero2.buerotage.add(wt3, wt4)

    def test_buero(self):
        """buero model tests"""
        buero1 = Buero.objects.first()
        buero2 = Buero.objects.last()

        self.assertEqual(buero1._permission_codename(), 'Buero_{}_editieren'.format(buero1.id))
        self.assertEqual(buero1._permission_name(), 'Büro Büro 1 verwalten')
        permission = Permission.objects.get(name=buero2._permission_name())
        self.assertEqual(permission.codename, buero2._permission_codename())
