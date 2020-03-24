from django.test import TestCase

from Klienten.forms import OrtChgForm


class OrtChgFormTest(TestCase):
    def test_chg_form_ort_field_label(self):
        form = OrtChgForm()
        self.assertTrue(form.fields['ort'].label == 'Ort')

    def test_chg_form_plz_field_label(self):
        form = OrtChgForm()
        self.assertTrue(form.fields['plz'].label == 'Plz')

    def test_chg_form_bus_field_help_text(self):
        form = OrtChgForm()
        self.assertEqual(form.fields['bus'].label, 'Bus')
