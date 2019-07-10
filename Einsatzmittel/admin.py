from django.contrib import admin

from .models import Bus, Buero

class BusAdmin(admin.ModelAdmin):
	ordering = ('bus',)
	list_display = ('bus', 'wird_verwaltet', 'fahrtage')

class BueroAdmin(admin.ModelAdmin):
	ordering = ('buero',)
	list_display = ('buero', 'wird_verwaltet', 'buerotage')	

admin.site.register(Bus, BusAdmin)
admin.site.register(Buero, BueroAdmin)

