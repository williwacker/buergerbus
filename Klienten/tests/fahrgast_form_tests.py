from django.test import TestCase

from Klienten.forms import FahrgastAddForm, FahrgastChgForm


class FahrgastChgFormTest(TestCase):
    def test_chg_form_name_field_label(self):
        form = FahrgastChgForm()
        self.assertTrue(form.fields['name'].label == 'Name')

    def test_chg_form_name_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['name'].help_text, 'Name, Vorname')

    def test_chg_form_telefon_field_label(self):
        form = FahrgastChgForm()
        self.assertTrue(form.fields['telefon'].label == 'Telefon')

    def test_chg_form_telefon_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['telefon'].help_text, '01234-1111')

    def test_chg_form_mobil_field_label(self):
        form = FahrgastChgForm()
        self.assertTrue(form.fields['mobil'].label == 'Mobil')

    def test_chg_form_mobil_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['mobil'].help_text, '0150-1111')

    def test_chg_form_ort_field_label(self):
        form = FahrgastChgForm()
        self.assertTrue(form.fields['ort'].label == 'Ort')

    def test_chg_form_strasse_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['strasse'].label, 'Strasse')

    def test_chg_form_hausnr_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['hausnr'].label, 'Hausnr')

    def test_chg_form_bemerkung_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['bemerkung'].label, 'Bemerkung')

    def test_chg_form_dsgvo_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['dsgvo'].label, 'DSGVO Status')

    def test_addf_form_typ_field_help_text(self):
        form = FahrgastAddForm()
        self.assertEqual(form.fields['typ'].label, 'Typ')

    def test_chg_form_bus_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(form.fields['bus'].label, 'Bus')

    def test_chg_form_bus_field_help_text(self):
        form = FahrgastChgForm()
        self.assertEqual(
            form.fields['bus'].help_text,
            'Dem Wohnort ist kein Bus zugeordnet. Deshalb für den Fahrgast einen Bus auswählen!')
