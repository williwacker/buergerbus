import json
from django.test import Client
from django.test import TestCase, RequestFactory
from Basis.tests import *
from Einsatzmittel.tests import *
from django.contrib.auth.models import User, Group, Permission
from ..models import Bus
from ..views import *

class BusListViewTests(TestCase):
    def setUp(self):
        UserTestCase().test_group()
        UserTestCase().test_user()
        BusTestCase().setUp()
        BusTestCase().test_bus()
        self.client = Client()
        self.user = User.objects.get(username='testuser')
        self.client.login(username='testuser', password='12345')
        self.group = Group.objects.get(name='Büro ABC')
        self.user.groups.add(self.group)
    
    def testListNoAddPerm(self):
        response = self.client.get('/Einsatzmittel/busse/', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('sidebar_liste', response.context)
        self.assertEqual(response.context['title'],'Busse')
        self.assertTemplateUsed(response, template_name='Basis/simple_table.html')
        self.assertNotIn('add', response.context)

    def testListWithAddPerm(self):
        self.group.permissions.add(Permission.objects.get(name='Can add Bus'))
        response = self.client.get('/Einsatzmittel/busse/', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['add'],'Bus')

    def testAddWithAddPerm(self):
        self.group.permissions.add(Permission.objects.get(name='Can add Bus'))
        factory = RequestFactory()
        request = factory.get('/Einsatzmittel/busse/add/', secure=True)
        request.user = self.user
        response = BusAddView.as_view()(request)
        self.assertEqual(response.status_code, 200)
#        self.assertIn('sidebar_liste', response.context)
#        self.assertEqual(response.context['title'],'Bus hinzufügen')
#        self.assertEqual(response.context['submit_button'],'Sichern')
#        self.assertEqual(response.context['back_button'],'Abbrechen')

    def testChangeNoDeletePerm(self):
        self.group.permissions.add(Permission.objects.get(name='Can change Bus'))
        bus_id = Bus.objects.first().id
        response = self.client.get('/Einsatzmittel/busse/'+str(bus_id)+'/', secure=True)
        self.assertEqual(response.status_code, 200)
#        self.assertIn('sidebar_liste', response.context)
#        self.assertEqual(response.context['title'],'Bus ändern')
#        self.assertEqual(response.context['submit_button'],'Sichern')
#        self.assertEqual(response.context['back_button'],'Abbrechen')
#        self.assertNotIn('delete_button', response.context)

    def testChangeWithDeletePerm(self):
        bus_id = Bus.objects.first().id
        self.group.permissions.add(Permission.objects.get(name='Can delete Bus'))
        response = self.client.get('/Einsatzmittel/busse/'+str(bus_id)+'/', secure=True)
        self.assertEqual(response.status_code, 200)
#        self.assertIn('sidebar_liste', response.context)
#        self.assertEqual(response.context['submit_button'],'Sichern')
#        self.assertEqual(response.context['back_button'],'Abbrechen')
#        self.assertEqual(response.context['delete_button'],'Löschen')

    def testDeleteWithDeletePerm(self):
        bus_id = Bus.objects.first().id
        response = self.client.get('/Einsatzmittel/busse/'+str(bus_id)+'/delete/', secure=True)
        self.assertEqual(response.status_code, 200)
#        self.assertIn('sidebar_liste', response.context)
#        self.assertEqual(response.context['title'],'Bus löschen')
#        self.assertEqual(response.context['submit_button'],'Ja, ich bin sicher')
#        self.assertEqual(response.context['back_button'],'Nein, bitte abbrechen')                  