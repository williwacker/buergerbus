from django.test import TestCase

from Basis.forms import FeedbackForm


class FeedbackFormTest(TestCase):
    def test_chg_form_an_field_label(self):
        form = FeedbackForm()
        self.assertEqual(form.fields['an'].label, 'An')

    def test_chg_form_betreff_field_label(self):
        form = FeedbackForm()
        self.assertEqual(form.fields['betreff'].label, 'Betreff')

    def test_chg_form_text_field_label(self):
        form = FeedbackForm()
        self.assertEqual(form.fields['text'].label, 'Text')
