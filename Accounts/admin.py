from django.contrib import admin
from django.contrib.auth.admin import User, UserAdmin
from Accounts.models import Profile

# Register your models here.


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

class ProfileAdmin(admin.ModelAdmin):
	ordering = ('user',)
	list_display = ('user','telefon','mobil')	        

admin.site.unregister(User)
admin.site.register(User, RestrictedUserAdmin)
admin.site.register(Profile, ProfileAdmin)
