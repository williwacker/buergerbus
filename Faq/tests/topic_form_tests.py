from django.test import TestCase

from Faq.forms import TopicAddForm

class TopicAddFormTest(TestCase):
    def test_add_form_name_field_label(self):
        form = TopicAddForm()
        self.assertEqual(form.fields['name'].label, 'Thema')

    def test_add_form_sort_order_field_label(self):
        form = TopicAddForm()
        self.assertEqual(form.fields['sort_order'].label, 'Sortierung')

    def test_add_form_sort_order_field_help_text(self):
        form = TopicAddForm()
        self.assertEqual(form.fields['sort_order'].help_text, 'Reihenfolge der Themen.')        
