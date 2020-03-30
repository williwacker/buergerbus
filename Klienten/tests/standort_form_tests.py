from django.test import TestCase

from Klienten.forms import StandortAddForm, StandortChgForm


class StandortChgFormTest(TestCase):
    def test_chg_form_name_field_label(self):
        form = StandortChgForm()
        self.assertTrue(form.fields['name'].label == 'Name')

    def test_chg_form_name_field_help_text(self):
        form = StandortChgForm()
        self.assertEqual(form.fields['name'].help_text, 'Name, Vorname')

    def test_chg_form_mobil_field_label(self):
        form = StandortChgForm()
        self.assertTrue(form.fields['mobil'].label == 'Mobil')

    def test_chg_form_mobil_field_help_text(self):
        form = StandortChgForm()
        self.assertEqual(form.fields['mobil'].help_text, '0150-1111')

    def test_chg_form_ort_field_label(self):
        form = StandortChgForm()
        self.assertTrue(form.fields['ort'].label == 'Ort')

    def test_chg_form_strasse_field_help_text(self):
        form = StandortChgForm()
        self.assertEqual(form.fields['strasse'].label, 'Strasse')

    def test_chg_form_hausnr_field_help_text(self):
        form = StandortChgForm()
        self.assertEqual(form.fields['hausnr'].label, 'Hausnr')
