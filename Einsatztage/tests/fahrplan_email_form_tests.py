from django.test import TestCase

from Einsatztage.forms import FahrplanEmailForm

class FahrplanEmailformTest(TestCase):
    def test_chg_form_von_field_label(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['von'].label, 'Von')

    def test_chg_form_an_field_label(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['an'].label, 'An')

    def test_chg_form_cc_field_label(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['cc'].label, 'Cc')

    def test_chg_form_cc_field_help_text(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['cc'].help_text, 'Email Adressen mit ; trennen')        

    def test_chg_form_betreff_field_label(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['betreff'].label, 'Betreff')

    def test_chg_form_text_field_label(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['text'].label, 'Text')

    def test_chg_form_datei_field_label(self):
        form = FahrplanEmailForm()
        self.assertEqual(form.fields['datei'].label, 'Datei(en)')
 