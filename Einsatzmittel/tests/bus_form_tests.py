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

    def test_add_form_fahrtage_field_label(self):
        form = BusAddForm()
        self.assertTrue(form.fields['fahrtage'].label == 'Fahrtage')

    def test_add_form_email_field_label(self):
        form = BusAddForm()
        self.assertEqual(form.fields['email'].label, 'Email')

    def test_add_form_planzeiten_field_label(self):
        form = BusAddForm()
        self.assertEqual(form.fields['planzeiten'].label, 'Fahrzeiten') 

    def test_add_form_planzeiten_field_help_text(self):
        form = BusAddForm()
        self.assertEqual(form.fields['planzeiten'].help_text, 'Mehrere Fahrzeiten durch Komma getrennt. Beispiel: 08:00-12:00, 14:00-17:00')               

    def test_add_form_standort_field_label(self):
        form = BusAddForm()
        self.assertEqual(form.fields['standort'].label, 'Bus Standort')
    