from django.conf import settings
from django.test import TestCase

#from Team.models import Fahrer
from Einsatzmittel.models import Bus, Wochentage
from Einsatzmittel.tests import BusTestCase
from Einsatztage.models import Fahrtag
from Einsatztage.utils import FahrtageSchreiben

#from Team.tests import FahrerTestCase

class FahrtagTestCase(TestCase):
    def setUp(self):
        BusTestCase().setUp()
#        FahrerTestCase().setUp()

    def test_fahrtag_no_driving_days(self):
        """Fahrtag model tests with count days=0"""
        setattr(settings, 'COUNT_DRIVING_DAYS', 0)
        setattr(settings, 'COUNT_TOUR_DAYS', 0)
        bus1 = Bus.objects.get(bus='Bus 1')
        bus1.plantage = 0
        bus1.save()
        bus2 = Bus.objects.get(bus='Bus 2')
        bus2.plantage = 0
        bus2.save()        
        FahrtageSchreiben().write_new_fahrtage()
        ft_count = Fahrtag.objects.filter(team=bus1, archiv=False).count()
        self.assertEqual(ft_count, 0)

    def test_fahrtag_with_driving_days(self):
        """Fahrtag model tests with count tour days"""
        setattr(settings, 'COUNT_DRIVING_DAYS', 0)
        setattr(settings, 'COUNT_TOUR_DAYS', 20)
        bus1= Bus.objects.get(bus="Bus 1")
        bus2 = Bus.objects.get(bus='Bus 2')
        bus2.plantage = 60
        bus2.save()        
        FahrtageSchreiben().write_new_fahrtage()
        ft_bus1_count = Fahrtag.objects.filter(team=bus1).count()
        ft_bus2_count = Fahrtag.objects.filter(team=bus2).count()
        ft_bus1 = Fahrtag.objects.filter(team=bus1).first()
        ft_bus2 = Fahrtag.objects.filter(team=bus2).first()
        self.assertEqual(ft_bus1.wochentag in ['Di','Do'], True)
        self.assertEqual(ft_bus2.wochentag in ['Mi','Fr'], True)
        self.assertGreater(ft_bus1_count, 0)
        self.assertGreater(ft_bus2_count, 0)
        self.assertGreater(ft_bus2_count, ft_bus1_count)
