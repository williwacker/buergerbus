import django_tables2 as tables
from datetime import datetime, date

from .models import Tour

class TourTable(tables.Table):
    fahrgast = tables.TemplateColumn(
        template_code='''
            {% if perms.Tour.change_tour %}
                {% if record.is_today %}
                    {{ record.klient |safe }}
                {% else %}
                    <a href="{{ record.id }}/{{ url_args }}">{{ record.klient |safe }}</a>
                {% endif %}
            {% else %}
                {{ record.klient |safe }}
            {% endif %}
        '''
    )
    uhrzeit = tables.TemplateColumn(
        template_code='''
            {% if record.has_conflict %}
                <span class="conflict">{{ record.uhrzeit }} {{ record.konflikt_richtung }}</span>
            {% else %}
                {{ record.uhrzeit }}
            {% endif %}
        '''
    )
    bemerkung = tables.TemplateColumn(
        template_code ='''{{ record.klient.bemerkung  |safe|default_if_none:""  }}<br/>{{ record.bemerkung|default_if_none:""  }} ''',
        orderable=False
    )
    class Meta:
        model = Tour
        fields = ('fahrgast','bus','datum','uhrzeit','zustieg','personenzahl','abholort','zielort','entfernung','ankunft','bemerkung')
