from django.test import TestCase

from Klienten.forms import StrassenChgForm


class StrassenChgFormTest(TestCase):
    def test_chg_form_ort_field_label(self):
        form = StrassenChgForm()
        self.assertTrue(form.fields['ort'].label == 'Ort')

    def test_chg_form_strasse_field_label(self):
        form = StrassenChgForm()
        self.assertTrue(form.fields['strasse'].label == 'Strasse')
