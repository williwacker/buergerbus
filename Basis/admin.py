from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin, User

class RestrictedUserAdmin(UserAdmin):
    model = User

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(RestrictedUserAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        user = kwargs['request'].user
        if not user.is_superuser:
            if db_field.name == 'groups':
                field.queryset = field.queryset.filter(id__in=[i.id for i in user.groups.all()])
            if db_field.name == 'user_permissions':
                field.queryset = field.queryset.filter(id__in=[i.id for i in user.user_permissions.all()])
            if db_field.name == 'is_superuser':
                field.widget.attrs['disabled'] = True
        return field

admin.site.unregister(User)
admin.site.register(User, RestrictedUserAdmin)