import django_tables2 as tables

from .models import Fahrtag, Buerotag

class FahrtagTable(tables.Table):
    datum = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.datum |safe }}</a>'''
    )
    class Meta:
        model = Fahrtag
        fields = ('datum','team','fahrer_vormittag','fahrer_nachmittag')

class BuerotagTable(tables.Table):
    datum = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.datum |safe }}</a>'''
    )
    class Meta:
        model = Buerotag
        fields = ('datum','team','mitarbeiter')