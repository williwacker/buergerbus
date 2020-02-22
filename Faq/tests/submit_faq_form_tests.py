from django.test import TestCase

from Faq.forms import SubmitFAQForm

class SubmitFAQFormTest(TestCase):
    def test_faq_form_topic_field_label(self):
        form = SubmitFAQForm()
        self.assertEqual(form.fields['topic'].label, 'Thema')

    def test_faq_form_text_field_label(self):
        form = SubmitFAQForm()
        self.assertEqual(form.fields['text'].label, 'Frage')

    def test_faq_form_text_field_help_text(self):
        form = SubmitFAQForm()
        self.assertEqual(form.fields['text'].help_text, 'Die aktuelle Frage.')

    def test_faq_form_answer_field_label(self):
        form = SubmitFAQForm()
        self.assertEqual(form.fields['answer'].label, 'Antwort')

    def test_faq_form_answer_field_help_text(self):
        form = SubmitFAQForm()
        self.assertEqual(form.fields['answer'].help_text, 'Die mögliche Antwort.')             
