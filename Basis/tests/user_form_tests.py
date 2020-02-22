from django.test import TestCase

from Basis.forms import MyUserCreationForm, MyUserChangeForm

class UserAddFormTest(TestCase):
    def test_add_form_username_field_label(self):
        form = MyUserCreationForm()
        self.assertEqual(form.fields['username'].label, 'Benutzername')

    def test_add_form_username_field_help_text(self):
        form = MyUserCreationForm()
        self.assertEqual(form.fields['username'].help_text, 'Erforderlich. 150 Zeichen oder weniger. Nur Buchstaben, Ziffern und @/./+/-/_.')        

    def test_add_form_first_name_field_label(self):
        form = MyUserCreationForm()
        self.assertEqual(form.fields['first_name'].label, 'Vorname')

    def test_add_form_last_name_field_label(self):
        form = MyUserCreationForm()
        self.assertEqual(form.fields['last_name'].label, 'Nachname')

    def test_add_form_email_field_label(self):
        form = MyUserCreationForm()
        self.assertEqual(form.fields['email'].label, 'E-Mail-Adresse')     

class UserChgFormTest(TestCase):
    def test_chg_form_username_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['username'].label, 'Benutzername')

    def test_chg_form_username_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['username'].help_text, 'Erforderlich. 150 Zeichen oder weniger. Nur Buchstaben, Ziffern und @/./+/-/_.')        

    def test_chg_form_first_name_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['first_name'].label, 'Vorname')

    def test_chg_form_last_name_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['last_name'].label, 'Nachname')

    def test_chg_form_email_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['email'].label, 'E-Mail-Adresse')
        
    def test_chg_form_groups_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['groups'].label, 'Gruppen')

    def test_chg_form_groups_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['groups'].help_text, 'Die Gruppen, denen der Benutzer angehört. Ein Benutzer bekommt alle Berechtigungen dieser Gruppen.')

    def test_chg_form_user_permissions_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['user_permissions'].label, 'Berechtigungen')    

    def test_chg_form_user_permissions_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['user_permissions'].help_text, 'Spezifische Berechtigungen für diesen Benutzer.')    

    def test_chg_form_is_staff_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['is_staff'].label, 'Mitarbeiter-Status')                    

    def test_chg_form_is_staff_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['is_staff'].help_text, 'Legt fest, ob sich der Benutzer an der Administrationsseite anmelden kann.')

    def test_chg_form_is_superuser_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['is_superuser'].label, 'Administrator-Status')                    

    def test_chg_form_is_superuser_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['is_superuser'].help_text, 'Legt fest, dass der Benutzer alle Berechtigungen hat, ohne diese einzeln zuweisen zu müssen.')            

    def test_chg_form_is_active_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['is_active'].label, 'Aktiv')                    

    def test_chg_form_is_active_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['is_active'].help_text, 'Legt fest, ob dieser Benutzer aktiv ist. Kann deaktiviert werden, anstatt Benutzer zu löschen.')            

    def test_chg_form_password_field_label(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['password'].label, 'Passwort')                    

    def test_chg_form_password_field_help_text(self):
        form = MyUserChangeForm()
        self.assertEqual(form.fields['password'].help_text, 'Die Passwörter werden nicht im Klartext gespeichert und können daher nicht dargestellt, sondern nur mit <a href="../password/">diesem Formular</a> geändert werden.')            
