from django.test import TestCase

from Faq.forms import QuestionChangeForm

class QuestionChangeFormTest(TestCase):
    def test_chg_form_text_field_label(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['text'].label, 'Frage')

    def test_chg_form_text_field_help_text(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['text'].help_text, 'Die aktuelle Frage.')

    def test_chg_form_answer_field_label(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['answer'].label, 'Antwort')

    def test_chg_form_answer_field_help_text(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['answer'].help_text, 'Die mögliche Antwort.')

    def test_chg_form_topic_field_label(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['topic'].label, 'Thema')

    def test_chg_form_status_field_label(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['status'].label, 'Status')

    def test_chg_form_status_field_help_text(self):
        form = QuestionChangeForm()
        self.assertEqual(form.fields['status'].help_text, 'Nur Fragen im Status \'Aktiv\' werden angezeigt. Fragen markiert als Gruppen Titel werden als solche behandelt.')
