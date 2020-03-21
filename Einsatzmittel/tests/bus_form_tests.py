from django.test import TestCase

from Einsatzmittel.forms import BusAddForm

class BusAddFormTest(TestCase):
    def test_add_form_bus_field_label(self):
        form = BusAddForm()
        self.assertTrue(form.fields['bus'].label == 'Bus')

    def test_add_form_plantage_field_label(self):
        form = BusAddForm()
        self.assertTrue(form.fields['plantage'].label == 'Planbare Kalendertage')

    def test_add_form_sitzplaetze_field_label(self):
        form = BusAddForm()
        self.assertTrue(form.fields['sitzplaetze'].label == 'Sitzplätze')

    def test_add_form_email_field_label(self):
        form = BusAddForm()
        self.assertEqual(form.fields['email'].label, 'Email')

    def test_add_form_fahrzeiten_field_label(self):
        form = BusAddForm()
        self.assertEqual(form.fields['fahrzeiten'].label, 'Fahrzeiten') 

    def test_add_form_standort_field_label(self):
        form = BusAddForm()
        self.assertEqual(form.fields['standort'].label, 'Bus Standort')
    