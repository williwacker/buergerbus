import django_tables2 as tables

from Basis.models import Document
from Tour.models import Tour


class DocumentTable(tables.Table):
    description = tables.TemplateColumn(
        template_code='''
			{% if perms.Basis.change_document %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.description |safe }}</a>
			{% else %}
				{{ record.description |safe }}
			{% endif %}
		'''
    )
    document = tables.TemplateColumn(
        template_code='''
			{% load my_tags %}
			<a href="{{ record.id }}/view/{{ record.relative_path }}" target="_blank">{{ record.document |safe }}</a>
		'''
    )

    class Meta:
        model = Document
        fields = ('description', 'document')


class TourStatisticTable(tables.Table):

    monat = tables.TemplateColumn(
        template_code='''
            {{ record.datum__datum__year }}/{{ record.datum__datum__month }}
        ''',
        orderable=False,
        verbose_name="Jahr/Monat"
    )
    bus = tables.TemplateColumn(
        template_code='''
            {{ record.bus__bus }}
        ''',
        verbose_name="Bus"
    )
    anzahl = tables.TemplateColumn(
        template_code='''
            {{ record.anzahl }}
        ''',
        verbose_name="Anzahl Touren"
    )

    class Meta:
        model = Tour
        fields = ('monat', 'bus', 'anzahl')


class KoordinatorStatisticTable(tables.Table):

    monat = tables.TemplateColumn(
        template_code='''
            {{ record.datum__datum__year }}/{{ record.datum__datum__month }}
        ''',
        orderable=False,
        verbose_name="Jahr/Monat"
    )
    koordinator = tables.TemplateColumn(
        template_code='''
            {{ record.created_by__last_name }}, {{ record.created_by__first_name }}
        ''',
        orderable=False,
        verbose_name="Koordinator"
    )
    anzahl = tables.TemplateColumn(
        template_code='''
            {{ record.anzahl }}
        ''',
        verbose_name="Anzahl gebuchte Touren"
    )

    class Meta:
        model = Tour
        fields = ('monat', 'koordinator', 'anzahl')
