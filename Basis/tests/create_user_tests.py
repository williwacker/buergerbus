from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from Accounts.models import MyUser, MyGroup


class UserTestCase(TestCase):
    def test_group(self):
        # create group and add permissions
        group, created = MyGroup.objects.get_or_create(name='Büro ABC')
        self.assertGreater(Permission.objects.all().count(), 0)
        group.permissions.add(Permission.objects.get(name='Can view Büro'))
        group.permissions.add(Permission.objects.get(name='Can view Bus'))
        group.permissions.add(Permission.objects.get(name='Can view Bürodienst'))
        group.permissions.add(Permission.objects.get(name='Can view Fahrdienst'))
#        id = ContentType.objects.get(model='question', app_label='Faq').id
#        print(Permission.objects.filter(content_type_id=id))
#        group.permissions.add(Permission.objects.get(name='Can view Fragen und Antworten', content_type_id=id))
#        group.permissions.add(Permission.objects.get(name='Can change Fragen und Antworten', content_type_id=id))
#        id = ContentType.objects.get(model='topic', app_label='Faq').id
#        group.permissions.add(Permission.objects.get(name='Can view Fragen und Antworten Thema', content_type_id=id))
#        group.permissions.add(Permission.objects.get(name='Can add Klient'))
#        group.permissions.add(Permission.objects.get(name='Can change Klient'))
        group.permissions.add(Permission.objects.get(name='Can view Klient'))
        group.permissions.add(Permission.objects.get(name='Can view Ort'))
        group.permissions.add(Permission.objects.get(name='Can view Strasse'))
        id = ContentType.objects.get(model='fahrer', app_label='Team').id
        group.permissions.add(Permission.objects.get(name='Can view Fahrer(in)', content_type_id=id))
        id = ContentType.objects.get(model='koordinator', app_label='Team').id
        group.permissions.add(Permission.objects.get(name='Can view Koordinator(in)', content_type_id=id))
        group.permissions.add(Permission.objects.get(name='Can view Tour'))

    def test_user(self):
        # create user and assign group permission
        user = MyUser.objects.create_user(username='testuser', password='12345',
                                        first_name='Test', last_name='User', email='bla@bla.de')
        self.assertTrue(user.is_active)
        group, created = MyGroup.objects.get_or_create(name='Büro ABC')
        user.groups.add(group)
        self.assertEqual(user.groups.count(), 1)
#        self.assertTrue(user.has_perm('Tour.add_tour'))
