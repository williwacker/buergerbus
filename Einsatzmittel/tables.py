import django_tables2 as tables

from .models import Bus, Buero

class BusTable(tables.Table):
    bus = tables.TemplateColumn(
        template_code='''<a href="{{ record.bus }}">{{ record.bus |safe }}</a>'''
    )
    class Meta:
        model = Bus
        fields = ('bus','sitzplaetze','fahrtage')

class BueroTable(tables.Table):
    buero = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.buero |safe }}</a>'''
    )
    class Meta:
        model = Buero
        fields = ('buero','buerotage')      