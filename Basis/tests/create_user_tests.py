from django.test import TestCase, Client
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class UserTestCase(TestCase):
    def test_group(self):
        # create group and add permissions
        group, created = Group.objects.get_or_create(name='Büro ABC')
        self.assertGreater(Permission.objects.all().count(), 0)
        group.permissions.add(Permission.objects.get(name='Can view Büro'))
        group.permissions.add(Permission.objects.get(name='Can view Bus'))
        group.permissions.add(Permission.objects.get(name='Can change Bürotag'))
        group.permissions.add(Permission.objects.get(name='Can view Bürotag'))
        group.permissions.add(Permission.objects.get(name='Can change Fahrtag'))
        group.permissions.add(Permission.objects.get(name='Can view Fahrtag'))
#        id = ContentType.objects.get(model='question', app_label='Faq').id
#        group.permissions.add(Permission.objects.get(name='Can add Frequent asked question', content_type_id=id))
#        group.permissions.add(Permission.objects.get(name='Can view Frequent asked question', content_type_id=id))
#        id = ContentType.objects.get(model='topic', app_label='Faq').id
#        group.permissions.add(Permission.objects.get(name='Can view Thema', content_type_id=id))
        group.permissions.add(Permission.objects.get(name='Can add Klient'))
        group.permissions.add(Permission.objects.get(name='Can change Klient'))
        group.permissions.add(Permission.objects.get(name='Can view Klient'))
        group.permissions.add(Permission.objects.get(name='Can delete Klient'))
        group.permissions.add(Permission.objects.get(name='Can add Ort'))
        group.permissions.add(Permission.objects.get(name='Can change Ort'))
        group.permissions.add(Permission.objects.get(name='Can view Ort'))
        group.permissions.add(Permission.objects.get(name='Can delete Ort'))
        group.permissions.add(Permission.objects.get(name='Can add Strasse'))
        group.permissions.add(Permission.objects.get(name='Can change Strasse'))
        group.permissions.add(Permission.objects.get(name='Can view Strasse'))
        group.permissions.add(Permission.objects.get(name='Can delete Strasse'))
#        id = ContentType.objects.get(model='fahrer', app_label='Team').id
#        group.permissions.add(Permission.objects.get(name='Can view Fahrer', content_type_id=id))
#        id = ContentType.objects.get(model='koordinator', app_label='Team').id
#        group.permissions.add(Permission.objects.get(name='Can view Koordinator', content_type_id=id))
        group.permissions.add(Permission.objects.get(name='Can add Tour'))
        group.permissions.add(Permission.objects.get(name='Can change Tour'))
        group.permissions.add(Permission.objects.get(name='Can view Tour'))
        group.permissions.add(Permission.objects.get(name='Can delete Tour'))


    def test_user(self):
        # create user and assign group permission
        user = User.objects.create_user(username='testuser', password='12345', first_name='Test', last_name='User', email='bla@bla.de')
        self.assertTrue(user.is_active)
        group, created = Group.objects.get_or_create(name='Büro ABC')
        user.groups.add(group)
        self.assertEqual(user.groups.count(), 1)
#        self.assertTrue(user.has_perm('Tour.add_tour'))
