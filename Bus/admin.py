from django.contrib import admin

from .models import Bus

class BusAdmin(admin.ModelAdmin):
	ordering = ('bus_id',)
	list_display = ('bus_id', 'wird_verwaltet', 'fahrtage')

admin.site.register(Bus, BusAdmin)

