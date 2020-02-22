import django_tables2 as tables
from django.conf import settings

from .models import Kommunen


class KommunenTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
            {% if perms.Kommunen.change_kommunen %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>
            {% else %}
                {{ record.name |safe }}
            {% endif %}            
        '''
    )

    class Meta:
        model = Kommunen
        fields = ('name', 'ansprechpartner', 'telefon', 'email', 'use_google', 'use_tour_hours', 
                  'send_dsgvo', 'allow_outside_clients', 'portal_name') 