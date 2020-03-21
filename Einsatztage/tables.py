import django_tables2 as tables

from Tour.models import Tour
from Team.models import Fahrer, Koordinator

from .models import Buerotag, Fahrtag


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
	fahrplan = tables.TemplateColumn(
		template_code='''
			{% if record.gaeste_vormittag > 0 or record.gaeste_nachmittag > 0 %}
				{% load static %}
				<a href="/Einsatztage/fahrer/{{ record.id }}/fahrplan/{{ url_args }}"><img src="{% static "project/img/fahrplan.png" %}" alt="Fahrplan anzeigen" title="Fahrplan anzeigen"></a>
				<a href="/Einsatztage/fahrer/{{ record.id }}/fahrplanAsPDF/" target="_blank"><img src="{% static "project/img/icon_pdf.png" %}" alt="Fahrplan als PDF anzeigen" title="Fahrplan als PDF anzeigen"></a>
				<!--a href="/Einsatztage/fahrer/{{ record.id }}/fahrplanAsCSV/"><img src="{% static "project/img/icon_pdf.png" %}" alt="Fahrplan als CSV speichern" title="Fahrplan als CSV anzeigen"></a-->
				{% if record.hat_fahrer %}
					<a href="/Einsatztage/fahrer/{{ record.id }}/fahrplanAsEmail/{{ url_args }}"><img src="{% static "project/img/send.png" %}" alt="Fahrplan verschicken" title="Fahrplan verschicken"></a>
				{% endif %}
			{% else %}
				&nbsp;
			{% endif %}
		''',orderable=False
	)
	gaeste_vormittag = tables.Column(orderable=False, verbose_name='Gäste')
	gaeste_nachmittag = tables.Column(orderable=False, verbose_name='Gäste')
	fahrer_vormittag = tables.TemplateColumn(
		template_code='''
			{% if record.gaeste_vormittag > 0 and record.fahrer_vormittag == None %}
				<span style="color:red; font-weight:bold">KEIN FAHRER EINGETEILT</span>
			{% elif record.urlaub %}
				<span style="color:green; font-weight:bold">URLAUB</span>
			{% else %}
				{{ record.fahrer_vormittag|default_if_none:'' }}
			{% endif %}
		'''
	)
	fahrer_nachmittag = tables.TemplateColumn(
		template_code='''
			{% if record.gaeste_nachmittag > 0 and record.fahrer_nachmittag == None %}
				<span style="color:red; font-weight:bold">KEIN FAHRER EINGETEILT</span>
			{% elif record.urlaub %}
				<span style="color:green; font-weight:bold">URLAUB</span>
			{% else %}
				{{ record.fahrer_nachmittag|default_if_none:'' }}
			{% endif %}
		'''
	)
	wochentag = tables.Column(
		orderable=False, verbose_name='Tag'
	)
	aktion_vormittag = tables.TemplateColumn(
		template_code='''
			{% load static %}
			{% if perms.Einsatztage.change_fahrtag and not record.urlaub %}
				{% if record.bookable_vormittag %}
					<a href="{{ record.id }}/bookv/{{ url_args }}">
						<img src="{% static "project/img/kalender-plus-32.png" %}" alt="Fahrtag am Vormittag für mich buchen" title="Fahrtag am Vormittag für mich buchen">
					</a>
				{% else %}
					{% ifequal record.fahrer_vormittag.benutzer user %}
						<a href="{{ record.id }}/cancelv/{{ url_args }}">
							<img src="{% static "project/img/kalender-minus-32.png" %}" alt="Fahrtag Buchung am Vormittag löschen" title="Fahrtag Buchung am Vormittag löschen">
						</a>
					{% endifequal %}
				{% endif %}
			{% endif %}
		''', orderable=False, verbose_name='Aktion'
	)
	aktion_nachmittag = tables.TemplateColumn(
		template_code='''
			{% load static %}
			{% if perms.Einsatztage.change_fahrtag and not record.urlaub %}
				{% if record.bookable_nachmittag %}
					<a href="{{ record.id }}/bookn/{{ url_args }}">
						<img src="{% static "project/img/kalender-plus-32.png" %}" alt="Fahrtag am Nachmittag für mich buchen" title="Fahrtag am Nachmittag für mich buchen">
					</a>
				{% else %}
					{% ifequal record.fahrer_nachmittag.benutzer user %}
						<a href="{{ record.id }}/canceln/{{ url_args }}">
							<img src="{% static "project/img/kalender-minus-32.png" %}" alt="Fahrtag Buchung am Nachmittag löschen" title="Fahrtag Buchung am Nachmittag löschen">
						</a>
					{% endifequal %}
				{% endif %}
			{% endif %}
		''', orderable=False, verbose_name='Aktion'
	)     

	class Meta:
		model = Fahrtag
		fields = ('datum','wochentag','team','fahrer_vormittag','aktion_vormittag','gaeste_vormittag','fahrer_nachmittag','aktion_nachmittag','gaeste_nachmittag','fahrplan')

	def before_render(self, request):
		if Fahrer.objects.filter(benutzer=request.user, aktiv=True).exists() \
		and request.user.has_perm('Einsatztage.change_fahrtag'):
			self.columns.show('aktion_vormittag')
			self.columns.show('aktion_nachmittag')
		else:
			self.columns.hide('aktion_vormittag')
			self.columns.hide('aktion_nachmittag')

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
	koordinator = tables.TemplateColumn(
		template_code='''
			{% if record.urlaub %}
				<span style="color:green; font-weight:bold">URLAUB</span>
			{% else %}
				{{ record.koordinator|default_if_none:'' }}
			{% endif %}
		'''
	) 
	wochentag = tables.Column(
		orderable=False
	)
	aktion = tables.TemplateColumn(
		template_code='''
			{% load static %}
			{% if perms.Einsatztage.change_buerotag and not record.urlaub %}
				{% if record.bookable %}
					<a href="{{ record.id }}/book/{{ url_args }}">
						<img src="{% static "project/img/kalender-plus-32.png" %}" alt="Bürotag für mich buchen" title="Bürotag für mich buchen">
					</a>
				{% else %}
					{% ifequal record.koordinator.benutzer user %}
						<a href="{{ record.id }}/cancel/{{ url_args }}">
							<img src="{% static "project/img/kalender-minus-32.png" %}" alt="Bürotag Buchung löschen" title="Bürotag Buchung löschen">
						</a>
					{% endifequal %}
				{% endif %}
			{% endif %}
		''', orderable=False
	)      

	class Meta:
		model = Buerotag
		fields = ('datum','wochentag','team','koordinator','aktion')

	def before_render(self, request):
		if Koordinator.objects.filter(benutzer=request.user, aktiv=True).exists() \
		and request.user.has_perm('Einsatztage.change_buerotag'):
			self.columns.show('aktion')
		else:
			self.columns.hide('aktion')


class TourTable(tables.Table):
	fahrgast = tables.TemplateColumn(
		template_code='''{{ record.klient |safe }}'''
	)
	bemerkungen = tables.TemplateColumn(
		template_code ='''
			{% if record.klient.bemerkung %}{{ record.klient.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% if record.bemerkung %}{{ record.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% ifnotequal record.klient  record.abholklient %}
				{% if record.abholklient.bemerkung %}{{ record.abholklient.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% endifnotequal %}
			{% ifnotequal record.klient  record.zielklient %}
				{% if record.zielklient.bemerkung %}{{ record.zielklient.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% endifnotequal %}
		''',
        attrs={"td": {"class": "remark"}}
	)
	telefon = tables.TemplateColumn(
		template_code='''{{ record.klient.telefon |default_if_none:"-" }}<br/>{{ record.klient.mobil |default_if_none:"" }}
		'''
	)
	abholort = tables.TemplateColumn(
		template_code='''{{ record.abholort | linebreaks }}'''
	)
	zielort = tables.TemplateColumn(
		template_code='''{{ record.zielort | linebreaks }}'''
	)		
	
	class Meta:
		model = Tour
		fields = ('fahrgast','telefon','uhrzeit','zustieg','personenzahl','abholort','zielort','entfernung','ankunft','bemerkungen')

class FahrerTable(tables.Table):
	class Meta:
		model = Fahrtag
		fields = ('fahrer_vormittag','fahrer_nachmittag')        
