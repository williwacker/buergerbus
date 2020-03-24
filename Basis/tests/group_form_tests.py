from django.test import TestCase

from Basis.forms import MyGroupChangeForm


class GroupChgFormTest(TestCase):
    def test_chg_form_name_field_label(self):
        form = MyGroupChangeForm()
        self.assertEqual(form.fields['name'].label, 'Name')

    def test_chg_form_berechtigungen_field_label(self):
        form = MyGroupChangeForm()
        self.assertEqual(form.fields['permissions'].label, 'Berechtigungen')
