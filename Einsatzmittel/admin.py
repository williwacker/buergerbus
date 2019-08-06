from django.contrib import admin

from .models import Bus, Buero

class BusAdmin(admin.ModelAdmin):
	ordering = ('bus',)
	list_display = ('bus', 'fahrtage', 'sitzplaetze', 'updated_by')

	def save_model(self, request, obj, form, change):
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)

class BueroAdmin(admin.ModelAdmin):
	ordering = ('buero',)
	list_display = ('buero', 'buerotage')	

admin.site.register(Bus, BusAdmin)
admin.site.register(Buero, BueroAdmin)

