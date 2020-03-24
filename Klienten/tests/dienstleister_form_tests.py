from django.test import TestCase

from Klienten.forms import (DienstleisterAddForm, DienstleisterChgForm,
                            KlientenSearchForm, KlientenSearchResultForm)


class DienstleisterChgFormTest(TestCase):
    def test_chg_form_name_field_label(self):
        form = DienstleisterChgForm()
        self.assertTrue(form.fields['name'].label == 'Name')

    def test_chg_form_name_field_help_text(self):
        form = DienstleisterChgForm()
        self.assertEqual(form.fields['name'].help_text, 'Name, Vorname')

    def test_chg_form_telefon_field_label(self):
        form = DienstleisterChgForm()
        self.assertTrue(form.fields['telefon'].label == 'Telefon')

    def test_chg_form_telefon_field_help_text(self):
        form = DienstleisterChgForm()
        self.assertEqual(form.fields['telefon'].help_text, '01234-1111')

    def test_chg_form_mobil_field_label(self):
        form = DienstleisterChgForm()
        self.assertTrue(form.fields['mobil'].label == 'Mobil')

    def test_chg_form_mobil_field_help_text(self):
        form = DienstleisterChgForm()
        self.assertEqual(form.fields['mobil'].help_text, '0150-1111')

    def test_chg_form_wohnort_field_label(self):
        form = DienstleisterChgForm()
        self.assertTrue(form.fields['ort'].label == 'Wohnort')

    def test_chg_form_strasse_field_label(self):
        form = DienstleisterChgForm()
        self.assertEqual(form.fields['strasse'].label, 'Strasse')

    def test_chg_form_hausnr_field_label(self):
        form = DienstleisterChgForm()
        self.assertEqual(form.fields['hausnr'].label, 'Hausnr')

    def test_chg_form_bemerkung_field_label(self):
        form = DienstleisterChgForm()
        self.assertEqual(form.fields['bemerkung'].label, 'Bemerkung')

    def test_add_form_typ_field_label(self):
        form = DienstleisterAddForm()
        self.assertEqual(form.fields['typ'].label, 'Typ')


class DienstleisterSearchFormTest(TestCase):
    def test_chg_form_suchname_field_label(self):
        form = KlientenSearchForm()
        self.assertTrue(form.fields['suchname'].label == 'Suchbegriff')

    def test_chg_form_suchname_field_help_text(self):
        form = KlientenSearchForm()
        self.assertEqual(form.fields['suchname'].help_text, 'z.B. Name, Gewerbe oder Telefonnummer')

    def test_chg_form_suchort_field_label(self):
        form = KlientenSearchForm()
        self.assertTrue(form.fields['suchort'].label == 'Ort')

    def test_chg_form_suchergebnis_field_label(self):
        form = KlientenSearchResultForm()
        self.assertEquals(form.fields['suchergebnis'].label, 'Suchergebnis')

    def test_chg_form_city_create_field_label(self):
        form = KlientenSearchResultForm()
        self.assertTrue(form.fields['city_create'].label == 'Ort und Strasse anlegen')

    def test_chg_form_city_create_field_help_text(self):
        form = KlientenSearchResultForm()
        self.assertTrue(form.fields['city_create'].help_text == 'Neuen Ort und/oder Strasse anlegen')

    def test_chg_form_force_create_field_label(self):
        form = KlientenSearchResultForm()
        self.assertTrue(form.fields['force_create'].label == 'Ähnlichkeit erlauben')

    def test_chg_form_force_create_field_help_text(self):
        form = KlientenSearchResultForm()
        self.assertTrue(
            form.fields['force_create'].help_text ==
            'Dienstleister anlegen, obwohl schon ein Eintrag mit ähnlichem Namen existiert')
