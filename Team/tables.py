import django_tables2 as tables

from .models import Buerokraft, Fahrer

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

class BuerokraftTable(tables.Table):
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.name |safe }}</a>'''
    )
    class Meta:
        model = Buerokraft
        fields = ('name','team','email','telefon')