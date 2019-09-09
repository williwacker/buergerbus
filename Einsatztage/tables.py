import django_tables2 as tables

from .models import Fahrtag, Buerotag
from Tour.models import Tour


class FahrtagTable(tables.Table):
    datum = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.datum |safe }}</a>'''
    )
    tour = tables.TemplateColumn(
        template_code='''
                        {% if record.gaeste_vormittag > 0 or record.gaeste_nachmittag > 0 %}
                            {% load static %}
                            <a href="/Einsatztage/fahrer/{{ record.id }}/tour/"><img src="{% static "project/img/fahrplan.png" %}" alt="Tour anzeigen" title="Tour anzeigen"></a>
                            <a href="/Einsatztage/fahrer/{{ record.id }}/tourAsPDF/"><img src="{% static "project/img/icon_pdf.png" %}" alt="PDF erzeugen" title="PDF erzeugen"></a>
                        {% else %}
                            &nbsp;
                        {% endif %}
                    '''
    )
    class Meta:
        model = Fahrtag
        fields = ('datum','team','fahrer_vormittag','gaeste_vormittag','fahrer_nachmittag','gaeste_nachmittag')

class BuerotagTable(tables.Table):
    datum = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.datum |safe }}</a>'''
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