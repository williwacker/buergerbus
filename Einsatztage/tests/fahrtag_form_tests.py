from django.test import TestCase

from Einsatztage.forms import FahrtagChgForm

class FahrtagChgFormTest(TestCase):
    def test_chg_form_datum_field_label(self):
        form = FahrtagChgForm()
        self.assertTrue(form.fields['datum'].label == 'Datum')

    def test_chg_form_team_field_label(self):
        form = FahrtagChgForm()
        self.assertTrue(form.fields['team'].label == 'Team')

    def test_chg_form_fahrer_vormittag_field_label(self):
        form = FahrtagChgForm()
        self.assertTrue(form.fields['fahrer_vormittag'].label == 'Fahrer Vormittag')

    def test_chg_form_fahrer_nachmittag_field_label(self):
        form = FahrtagChgForm()
        self.assertTrue(form.fields['fahrer_nachmittag'].label == 'Fahrer Nachmittag')

    def test_chg_form_urlaub_field_label(self):
        form = FahrtagChgForm()
        self.assertTrue(form.fields['urlaub'].label == 'Urlaub')
    