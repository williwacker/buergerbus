from django.test import TestCase

from Basis.forms import DocumentAddForm, DocumentChangeForm


class DocumentAddFormTest(TestCase):
    def test_add_form_description_field_label(self):
        form = DocumentAddForm()
        self.assertEqual(form.fields['description'].label, 'Beschreibung')

    def test_add_form_document_field_label(self):
        form = DocumentAddForm()
        self.assertEqual(form.fields['document'].label, 'Dokument')


class DocumentChgFormTest(TestCase):
    def test_chg_form_description_field_label(self):
        form = DocumentChangeForm()
        self.assertEqual(form.fields['description'].label, 'Beschreibung')

    def test_chg_form_document_ro_field_label(self):
        form = DocumentChangeForm()
        self.assertEqual(form.fields['document_ro'].label, 'Dokument')
