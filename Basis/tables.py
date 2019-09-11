import django_tables2 as tables

from django.contrib.auth.models import User, Group

class UserTable(tables.Table):
    username = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.username |safe }}</a>'''
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active')

class GroupTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''<a href="{{ record.id }}">{{ record.name |safe }}</a>'''
    )
    class Meta:
        model = Group
        fields = ('name', )        

  