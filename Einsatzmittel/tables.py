import django_tables2 as tables

from .models import Buero, Bus


class BusTable(tables.Table):
    bus = tables.TemplateColumn(
        template_code='''
            {% if perms.Einsatzmittel.change_bus %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.bus |safe }}</a>
            {% else %}
                {{ record.bus |safe }}
            {% endif %}
        '''
    )
    fahrzeiten = tables.TemplateColumn(
        template_code='''
            {% for object in record.fahrzeiten.all %}
                {{ object }}<br>
            {% endfor %}
        '''
    )

    class Meta:
        model = Bus
        fields = ('bus', 'plantage', 'plan_ende', 'sitzplaetze', 'fahrzeiten', 'email', 'standort')


class BueroTable(tables.Table):
    buero = tables.TemplateColumn(
        template_code='''
        {% if perms.Einsatzmittel.change_buero %}
            <a href="{{ record.id }}/{{ url_args }}">{{ record.buero |safe }}</a>
        {% else %}
                {{ record.buero |safe }}
        {% endif %}
        '''
    )

    class Meta:
        model = Buero
        fields = ('buero', 'plantage', 'plan_ende', 'buerotage', 'email')
