import django_tables2 as tables
from django.conf import settings

from .models import Klienten, Orte, Strassen


class FahrgaesteTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
            {% if perms.Klienten.change_klienten %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>
            {% else %}
                {{ record.name |safe }}
            {% endif %}            
        '''
    )
    adresse = tables.TemplateColumn(
        template_code='''{{ record.ort }}<br/>{{ record.strasse }} {{ record.hausnr }}''',
        orderable=False
    )
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )
    bemerkung = tables.TemplateColumn(
        template_code='''{{ record.bemerkung }}''',
        attrs={"td": {"class": "remark"}}
    )
    dsgvo = tables.TemplateColumn('''
        {% load static %}
        {% if record.dsgvo == '01' %}
            <img src="{% static "project/img/dsgvo.png" %}" alt="DSGVO erstellt" title="DSGVO erstellt">
            <a href="{{ record.id }}/dsgvoAsPDF/" target="_blank"><img src="{% static "project/img/icon_pdf.png" %}" alt="DSGVO als PDF anzeigen" title="DSGVO als PDF anzeigen/herunterladen"></a>
        {% else %}
            {% if record.dsgvo == '02' %}
                <img src="{% static "project/img/pencil.png" %}" alt="DSGVO zur Unterschrift" title="DSGVO zur Unterschrift">
            {% else %}
                <img src="{% static "project/img/checkmark.png" %}" alt="DSGVO liegt vor" title="DSGVO liegt vor">
            {% endif %}
        {% endif %}  
        ''',
                                  orderable=False
                                  )
    tour = tables.TemplateColumn('''
        {% load static %}
        {% if record.bus %}
            <a href="/Tour/tour/add/{{ record.id }}/"><img src="{% static "project/img/fahrplan.png" %}" alt="Tour hinzuf&uuml;gen" title="Tour hinzuf&uuml;gen"></a>
        {% endif %}
        ''',
                                 orderable=False
                                 )
    anzahl_fahrgast_touren = tables.TemplateColumn(
        template_code='''{{ record.anzahl_fahrgast_touren }}''',
        orderable=False,
        verbose_name='Anzahl Touren'
    )

    class Meta:
        model = Klienten
        fields = ('tour', 'name', 'telefon', 'adresse', 'bus', 'bemerkung', 'dsgvo', 'anzahl_fahrgast_touren')

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('anzahl_fahrgast_touren')
        else:
            self.columns.hide('anzahl_fahrgast_touren')

        if settings.SEND_DSGVO:
            self.columns.show('dsgvo')
        else:
            self.columns.hide('dsgvo')


class DienstleisterTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
            {% if perms.Klienten.change_klienten %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>
            {% else %}
                {{ record.name |safe }}
            {% endif %}                  
        '''
    )
    adresse = tables.TemplateColumn(
        template_code='''{{ record.ort }}<br/>{{ record.strasse }} {{ record.hausnr }}''',
        orderable=False
    )
    telefon = tables.TemplateColumn(
        template_code='''{{ record.telefon |default_if_none:"-" }}<br/>{{ record.mobil |default_if_none:"" }}'''
    )
    bemerkung = tables.TemplateColumn(
        template_code='''{{ record.bemerkung|default_if_none:"-" }}''',
        attrs={"td": {"class": "remark"}}
    )
    anzahl_dienstleister_touren = tables.TemplateColumn(
        template_code='''{{ record.anzahl_dienstleister_touren }}''',
        orderable=False,
        verbose_name='Anzahl Touren'
    )

    class Meta:
        model = Klienten
        fields = ('name', 'telefon', 'adresse', 'bemerkung', 'kategorie', 'anzahl_dienstleister_touren')

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('anzahl_dienstleister_touren')
        else:
            self.columns.hide('anzahl_dienstleister_touren')


class StandorteTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
            {% if perms.Klienten.change_klienten %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>
            {% else %}
                {{ record.name |safe }}
            {% endif %}            
        '''
    )
    adresse = tables.TemplateColumn(
        template_code='''{{ record.ort }}<br/>{{ record.strasse }} {{ record.hausnr }}''',
        orderable=False
    )
    telefon = tables.TemplateColumn(
        template_code='''{{ record.mobil |default_if_none:"" }}'''
    )

    class Meta:
        model = Klienten
        fields = ('name', 'telefon', 'adresse')


class OrteTable(tables.Table):
    ort = tables.TemplateColumn(
        template_code='''
            {% if perms.Klienten.change_orte %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.ort |safe }}</a>
            {% else %}
                {{ record.ort |safe }}
            {% endif %}     
        '''
    )

    class Meta:
        model = Orte
        fields = ('ort', 'plz', 'bus')


class StrassenTable(tables.Table):
    ort = tables.TemplateColumn(
        template_code='''
            {% if perms.Klienten.change_strassen %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.ort |safe }}</a>
            {% else %}
                {{ record.ort |safe }}
            {% endif %} 
        '''
    )

    class Meta:
        model = Strassen
        fields = ('ort', 'strasse')
