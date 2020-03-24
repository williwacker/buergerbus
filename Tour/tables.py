from datetime import date, datetime

import django_tables2 as tables

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
    datum = tables.TemplateColumn(
        template_code='''
		{{ record.datum }}
		'''
    )
    uhrzeit = tables.TemplateColumn(
        template_code='''
			{% if record.has_conflict %}
				<span class="conflict">{{ record.uhrzeit }}</span>
				{{ record.konflikt_zeiten|linebreaksbr }}
			{% else %}
				{{ record.uhrzeit }}
			{% endif %}
		'''
    )
    abholort = tables.TemplateColumn(
        template_code='''
		{{ record.abholort|linebreaksbr }}
		'''
    )
    zielort = tables.TemplateColumn(
        template_code='''
		{{ record.zielort|linebreaksbr }}
		'''
    )
    bemerkungen = tables.TemplateColumn(
        template_code='''
			{% if record.klient.bemerkung %}{{ record.klient.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% if record.termin %}
				<span style="background-color:yellow;">Termin: {{ record.termin }}</span><br/>
			{% endif %}
			{% if record.bemerkung %}
				{% if record.has_markup_text %}<span style="background-color:yellow;">{% endif %}
					{{ record.bemerkung|default_if_none:"" }}<br/>
				{% if record.has_markup_text %}</span>{% endif %}					
			{% endif %}
			{% ifnotequal record.klient  record.abholklient %}
				{% if record.abholklient.bemerkung %}{{ record.abholklient.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% endifnotequal %}
			{% ifnotequal record.klient  record.zielklient %}
				{% if record.zielklient.bemerkung %}{{ record.zielklient.bemerkung|default_if_none:"" }}<br/>{% endif %}
			{% endifnotequal %}
		''',
        orderable=False,
        attrs={"td": {"class": "remark"}}
    )
    aktion = tables.TemplateColumn(
        template_code='''
			{% if perms.Tour.add_tour %}
				{% load static %}
				<a href="{{ record.id }}/copy/">
					<img src="{% static "project/img/icon_duplicate_32.png" %}" alt="Tour kopieren" title="Tour kopieren">
				</a>
			{% endif %}
			{% if perms.Tour.change_tour %}
				{% load my_tags %}
				{% if record.konflikt_richtung|in_list:'U,D' %}
					{% load static %}
					<a href="{{ record.id }}/accept/">
						<img src="{% static "project/img/checkmark.png" %}" alt="Vorgeschlagene Abholzeit übernehmen" title="Vorgeschlagene Abholzeit übernehmen">
					</a>
				{% endif %}
			{% endif %}
		''', orderable=False
    )

    class Meta:
        model = Tour
        fields = ('fahrgast', 'bus', 'datum', 'uhrzeit', 'zustieg', 'personenzahl',
                  'abholort', 'zielort', 'entfernung', 'ankunft', 'bemerkungen', 'aktion')

    def before_render(self, request):
        if request.user.has_perm('Tour.change_tour'):
            self.columns.show('aktion')
        else:
            self.columns.hide('aktion')
