from django.test import TestCase

from Einsatzmittel.forms import BueroAddForm

class BueroAddFormTest(TestCase):
    def test_add_form_buero_field_label(self):
        form = BueroAddForm()
        self.assertTrue(form.fields['buero'].label == 'Büro')

    def test_add_form_buerotage_field_label(self):
        form = BueroAddForm()
        self.assertTrue(form.fields['buerotage'].label == 'Bürotage')

    def test_add_form_email_field_label(self):
        form = BueroAddForm()
        self.assertEqual(form.fields['email'].label, 'Email')
