import django_tables2 as tables

from .models import Fahrer, Koordinator
from django.contrib.auth.models import User

class FahrerTable(tables.Table):
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.name |safe }}</a>'''
    )
    email = tables.TemplateColumn(
        template_code='''<a href="mailto:{{ record.email }}">{{ record.email }}</a>'''
    )        
    class Meta:
        model = Fahrer
        fields = ('name','team','email','telefon')

class KoordinatorTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.benutzer.last_name }},&nbsp;{{ record.benutzer.first_name }}</a>''',
        orderable=False
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
        fields = ('name','team','email','telefon')