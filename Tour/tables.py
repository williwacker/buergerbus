import django_tables2 as tables
from datetime import datetime, date

from .models import Tour

class TourTable(tables.Table):
    fahrgast = tables.TemplateColumn(
        template_code='''
            {% if record.is_today %}
                {{ record.klient |safe }}
            {% else %}
                <a href="{{ record.id }}">{{ record.klient |safe }}</a>
            {% endif %}
        '''
    )
    class Meta:
        model = Tour
        fields = ('fahrgast','bus','datum','uhrzeit','abholort','zielort','entfernung','ankunft')
