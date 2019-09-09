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
    class Meta:
        model = Fahrer
        fields = ('name','team','email','telefon')

class KoordinatorTable(tables.Table):
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.benutzer.last_name }},&nbsp;{{ record.benutzer.first_name }}</a>'''
    )
    email = tables.TemplateColumn(
        template_code='''{{ record.benutzer.email }}'''
    )    
    class Meta:
        model = Koordinator
        fields = ('name','team','email','telefon')