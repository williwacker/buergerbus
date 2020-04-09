from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from Basis.tests import *

from ..models import MyGroup


class GroupListViewTests(TestCase):
	model = MyGroup
	list_url = '/Accounts/gruppen/'
	title = 'Gruppe'
	title_plural = 'Gruppen'

	def setUp(self):
		UserTestCase().test_group()
		UserTestCase().test_user()

		self.client = Client()
		self.user = User.objects.get(username='testuser')
		self.client.login(username='testuser', password='12345')
		self.group = Group.objects.get(name='Büro ABC')
		id = str(self.model.objects.first().id)
		self.user.groups.add(self.group)
		self.add_url = self.list_url+'add/'
		self.change_url = self.list_url+id+'/'
		self.delete_url = self.list_url+id+'/'+'delete/'
		self.contentTypeId = ContentType.objects.get(model='group').id

	def testListNoAddPerm(self):
		self.group.permissions.add(Permission.objects.get(name='Can view group', content_type_id=self.contentTypeId))
		response = self.client.get(self.list_url, secure=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn('sidebar_liste', response.context)
		self.assertEqual(response.context['title'], self.title_plural)
		self.assertTemplateUsed(response, template_name='Basis/simple_table.html')
		self.assertNotIn('add', response.context)

	def testListWithAddPerm(self):
		self.group.permissions.add(Permission.objects.get(name='Can view group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can add group', content_type_id=self.contentTypeId))
		response = self.client.get(self.list_url, secure=True)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['add'], self.title)

	def testAddWithAddPerm(self):
		self.group.permissions.add(Permission.objects.get(name='Can view group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can add group', content_type_id=self.contentTypeId))
		response = self.client.get(self.add_url, secure=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn('sidebar_liste', response.context)
		self.assertEqual(response.context['title'], self.title+' hinzufügen')
		self.assertEqual(response.context['submit_button'], 'Sichern')
		self.assertEqual(response.context['back_button'], ['Abbrechen', self.list_url])

	def testChangeNoDeletePerm(self):
		self.group.permissions.add(Permission.objects.get(name='Can view group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can change group', content_type_id=self.contentTypeId))
		response = self.client.get(self.change_url, secure=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn('sidebar_liste', response.context)
		self.assertEqual(response.context['title'], self.title+' ändern')
		self.assertEqual(response.context['submit_button'], 'Sichern')
		self.assertEqual(response.context['back_button'], ['Abbrechen', self.list_url])
		self.assertNotIn('delete_button', response.context)

	def testChangeWithDeletePerm(self):
		self.group.permissions.add(Permission.objects.get(name='Can view group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can change group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can delete group', content_type_id=self.contentTypeId))
		response = self.client.get(self.change_url, secure=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn('sidebar_liste', response.context)
		self.assertEqual(response.context['submit_button'],'Sichern')
		self.assertEqual(response.context['back_button'],['Abbrechen',self.list_url])
		self.assertEqual(response.context['delete_button'],'Löschen')

	def testDeleteWithDeletePerm(self):
		self.group.permissions.add(Permission.objects.get(name='Can view group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can change group', content_type_id=self.contentTypeId))
		self.group.permissions.add(Permission.objects.get(name='Can delete group', content_type_id=self.contentTypeId))
		response = self.client.get(self.delete_url, secure=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn('sidebar_liste', response.context)
		self.assertEqual(response.context['title'],self.title+' löschen')
#		self.assertEqual(response.context['submit_button'],'Ja, ich bin sicher')
#		self.assertEqual(response.context['back_button'],'Nein, bitte abbrechen')
