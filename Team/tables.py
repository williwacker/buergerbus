import django_tables2 as tables
from django.contrib.auth.models import User

from .models import Fahrer, Koordinator


class FahrerTable(tables.Table):
	name = tables.TemplateColumn(
		template_code='''
			{% if perms.Team.change_fahrer %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.benutzer.last_name }},&nbsp;{{ record.benutzer.first_name }}</a>
			{% else %}
				{{ record.benutzer.last_name }},&nbsp;{{ record.benutzer.first_name }}
			{% endif %}
		'''
	)
	telefon = tables.TemplateColumn(
		template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
	)    
	email = tables.TemplateColumn(
		template_code='''<a href="mailto:{{ record.benutzer.email }}">{{ record.benutzer.email }}</a>''',
		orderable=False
	)
	aktion = tables.TemplateColumn(
		template_code='''
			{% load static %}
			{% if perms.Team.add_fahrer %}
				<a href="{{ record.id }}/copy/">
					<img src="{% static "project/img/icon_duplicate_32.png" %}" alt="Fahrer kopieren" title="Fahrer kopieren">
				</a>
			{% endif %}
		''', orderable=False
	)    

	class Meta:
		model = Fahrer
		fields = ('name','team','email','telefon','aktiv','aktion')

	def before_render(self, request):
		if request.user.has_perm('Team.change_fahrer'):
			self.columns.show('aktion')
		else:
			self.columns.hide('aktion')		

class KoordinatorTable(tables.Table):
	name = tables.TemplateColumn(
		template_code='''
			{% if perms.Team.change_koordinator %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.benutzer.last_name }},&nbsp;{{ record.benutzer.first_name }}</a>
			{% else %}
				{{ record.benutzer.last_name }},&nbsp;{{ record.benutzer.first_name }}
			{% endif %}
		''',orderable=False
	)
	telefon = tables.TemplateColumn(
		template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
	)
	email = tables.TemplateColumn(
		template_code='''<a href="mailto:{{ record.benutzer.email }}">{{ record.benutzer.email }}</a>''',
		orderable=False
	)
	   
	class Meta:
		model = Koordinator
		fields = ('name','team','email','telefon','aktiv')
