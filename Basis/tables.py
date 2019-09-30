import django_tables2 as tables

from django.contrib.auth.models import User, Group

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
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active')

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
        model = Group
        fields = ('name', )        

  