import django_tables2 as tables

from .models import MyGroup, MyUser, Profile


class UserTable(tables.Table):
    benutzer = tables.TemplateColumn(
        template_code='''
			{% if perms.auth.change_user %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.user |safe }}</a>
			{% else %}
				{{ record.user |safe }}
			{% endif %}
		'''
    )

    class Meta:
        model = MyUser
        fields = ('benutzer', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active')

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


class ProfileTable(tables.Table):
    benutzer = tables.TemplateColumn(
        template_code='''
			{% if perms.auth.change_user %}
				<a href="{{ record.id }}/{{ url_args }}">{{ record.user |safe }}</a>
			{% else %}
				{{ record.user |safe }}
			{% endif %}
		'''
    )

    class Meta:
        model = Profile
        fields = ('benutzer', 'telefon', 'mobil')
