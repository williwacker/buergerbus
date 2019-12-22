from django.contrib import admin

from .models import Fahrer, Koordinator


class FahrerAdmin(admin.ModelAdmin):
	
    list_display = ('benutzer', 'team', 'mobil', 'aktiv')
    list_filter = ('team',)
    list_editable = ('mobil',)
    ordering = ('benutzer',)

    def get_queryset(self, request):
        qs = super(FahrerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(aktiv=True)

admin.site.register(Fahrer, FahrerAdmin)        

# ...............

class KoordinatorAdmin(admin.ModelAdmin):
	
    list_display = ('benutzer', 'name', 'team', 'mobil', 'aktiv')
    list_filter = ('team',)
    list_editable = ('mobil',)
    ordering = ('benutzer',)

    def name(self, obj):
        return ", ".join([obj.benutzer.last_name,obj.benutzer.first_name])

    def get_queryset(self, request):
        qs = super(KoordinatorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(aktiv=True)        

admin.site.register(Koordinator, KoordinatorAdmin)
