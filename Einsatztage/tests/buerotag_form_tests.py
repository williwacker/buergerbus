from django.test import TestCase

from Einsatztage.forms import BuerotagChgForm

class BuerotagChgFormTest(TestCase):
    def test_chg_form_datum_field_label(self):
        form = BuerotagChgForm()
        self.assertTrue(form.fields['datum'].label == 'Datum')

    def test_chg_form_team_field_label(self):
        form = BuerotagChgForm()
        self.assertTrue(form.fields['team'].label == 'Team')

    def test_chg_form_koordinator_field_label(self):
        form = BuerotagChgForm()
        self.assertTrue(form.fields['koordinator'].label == 'Koordinator')

    def test_chg_form_urlaub_field_label(self):
        form = BuerotagChgForm()
        self.assertTrue(form.fields['urlaub'].label == 'Urlaub')
    