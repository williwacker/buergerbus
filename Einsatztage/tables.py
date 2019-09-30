import django_tables2 as tables

from .models import Fahrtag, Buerotag
from Tour.models import Tour


class FahrtagTable(tables.Table):
    datum = tables.TemplateColumn(
        template_code='''
            {% if perms.Einsatztage.change_fahrtag %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.datum |safe }}</a>
            {% else %}
                {{ record.datum |safe }}
            {% endif %}
        '''
    )
    tour = tables.TemplateColumn(
        template_code='''
            {% if record.gaeste_vormittag > 0 or record.gaeste_nachmittag > 0 %}
                {% load static %}
                <a href="/Einsatztage/fahrer/{{ record.id }}/fahrplan/"><img src="{% static "project/img/fahrplan.png" %}" alt="Fahrplan anzeigen" title="Fahrplan anzeigen"></a>
                <a href="/Einsatztage/fahrer/{{ record.id }}/fahrplanAsPDF/"><img src="{% static "project/img/icon_pdf.png" %}" alt="Fahrplan als PDF erzeugen" title="Fahrplan als PDF erzeugen"></a>
                {% if record.hat_fahrer %}
                    <a href="/Einsatztage/fahrer/{{ record.id }}/fahrplanAsEmail/"><img src="{% static "project/img/send.png" %}" alt="Fahrplan als Email verschicken" title="Fahrplan als Email verschicken"></a>
                {% endif %}
            {% else %}
                &nbsp;
            {% endif %}
        ''',orderable=False
    )
    gaeste_vormittag = tables.Column(orderable=False)
    gaeste_nachmittag = tables.Column(orderable=False)
    fahrer_vormittag = tables.TemplateColumn(
        template_code='''
            {% if record.gaeste_vormittag > 0 and record.fahrer_vormittag == None %}
                <span style="color:red; font-weight:bold">KEIN FAHRER EINGETEILT</span>
            {% else %}
                {{ record.fahrer_vormittag|default_if_none:'' }}
            {% endif %}
        '''
    )
    fahrer_nachmittag = tables.TemplateColumn(
        template_code='''
            {% if record.gaeste_nachmittag > 0 and record.fahrer_nachmittag == None %}
                <span style="color:red; font-weight:bold">KEIN FAHRER EINGETEILT</span>
            {% else %}
                {{ record.fahrer_nachmittag|default_if_none:'' }}
            {% endif %}
        '''
    )
    wochentag = tables.Column(orderable=False)
    class Meta:
        model = Fahrtag
        fields = ('datum','wochentag','team','fahrer_vormittag','gaeste_vormittag','fahrer_nachmittag','gaeste_nachmittag','tour')

class BuerotagTable(tables.Table):
    datum = tables.TemplateColumn(
        template_code='''
            {% if perms.Einsatztage.change_buerotag %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.datum |safe }}</a>
            {% else %}
                {{ record.datum |safe }}
            {% endif %}            
        '''
    )
    class Meta:
        model = Buerotag
        fields = ('datum','team','koordinator')


class TourTable(tables.Table):
    fahrgast = tables.TemplateColumn(
        template_code='''{{ record.klient |safe }}'''
    )
    bemerkungen = tables.TemplateColumn(
        template_code='''{{ record.klient.bemerkung |default_if_none:'' }}<br>{{ record.bemerkung |default_if_none:'' }}'''
    )
    telefon = tables.TemplateColumn(
        template_code='''{{ record.klient.telefon |default_if_none:"-" }}<br/>{{ record.klient.mobil |default_if_none:"" }}'''
    )
    class Meta:
        model = Tour
        fields = ('fahrgast','telefon','uhrzeit','abholort','zielort','entfernung','ankunft','bemerkungen')

class FahrerTable(tables.Table):
    class Meta:
        model = Fahrtag
        fields = ('fahrer_vormittag','fahrer_nachmittag')        