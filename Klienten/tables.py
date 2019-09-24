import django_tables2 as tables

from .models import Orte, Strassen, Klienten

class FahrgaesteTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>'''
    )
    adresse = tables.TemplateColumn(
        template_code='''{{ record.ort }}<br/>{{ record.strasse }} {{ record.hausnr }}''',
        orderable=False
    )
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )
    dsgvo = tables.TemplateColumn('''
        {% load static %}
        {% if record.dsgvo == '01' %}
            <a href="{{ record.id }}/dsgvo/"><img src="{% static "project/img/dsgvo.png" %}" alt="DSGVO anzeigen" title="DSGVO anzeigen"></a>
            <a href="{{ record.id }}/dsgvoAsPDF/"><img src="{% static "project/img/icon_pdf.png" %}" alt="PDF erzeugen" title="PDF erzeugen"></a>
        {% else %}
            {% if klient.dsgvo == '02' %}
                <img src="{% static "project/img/pencil.png" %}" alt="DSGVO zur Unterschrift" title="DSGVO zur Unterschrift">
            {% else %}
                <img src="{% static "project/img/checkmark.png" %}" alt="DSGVO liegt vor" title="DSGVO liegt vor">
            {% endif %}
        {% endif %}  
        ''',
        orderable=False)
    class Meta:
        model = Klienten
        fields = ('name','telefon','adresse','bus','bemerkung','dsgvo')

class DienstleisterTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>'''
    )
    adresse = tables.TemplateColumn(
       template_code='''{{ record.ort }}<br/>{{ record.strasse }} {{ record.hausnr }}''',
       orderable=False
    )
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )   
    class Meta:
        model = Klienten
        fields = ('name','telefon','adresse','bemerkung','kategorie')

        
class OrteTable(tables.Table):
    ort = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}/{{ url_args }}">{{ record.ort |safe }}</a>'''
    )
    class Meta:
        model = Orte
        fields = ('ort','bus')

class StrassenTable(tables.Table):
    ort = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}/{{ url_args }}">{{ record.ort |safe }}</a>'''
    )
    class Meta:
        model = Strassen
        fields = ('ort','strasse')       