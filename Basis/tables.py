import django_tables2 as tables

from Basis.models import Document
from Tour.models import Tour

from .models import MyGroup, MyUser


class UserTable(tables.Table):
    username = tables.TemplateColumn(
        template_code='''
			{% if perms.auth.change_user %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.username |safe }}</a>
			{% else %}
				{{ record.username |safe }}
			{% endif %}
		'''
    )

    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active')

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('is_staff')
            self.columns.show('is_superuser')
        else:
            self.columns.hide('is_staff')
            self.columns.hide('is_superuser')


class GroupTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
			{% if perms.auth.change_group %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>
			{% else %}
				{{ record.name |safe }}
			{% endif %}
		'''
    )

    class Meta:
        model = MyGroup
        fields = ('name', )


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
