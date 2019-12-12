from django.contrib import admin

from .models import Buero, Bus, Wochentage


class BusAdmin(admin.ModelAdmin):
	ordering = ('bus',)
	list_display = ('bus', 'sitzplaetze', 'updated_by')
	readonly_fields = ('updated_by',)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if not request.user.is_superuser:
			if db_field.name == "bus":
				kwargs["queryset"] = get_bus_qs(request)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def save_model(self, request, obj, form, change):
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)

class BueroAdmin(admin.ModelAdmin):
	ordering = ('buero',)
	list_display = ('buero',)	

class WochentageAdmin(admin.ModelAdmin):
	ordering = ('id', )
	list_display = ('name', )


admin.site.register(Bus, BusAdmin)
admin.site.register(Buero, BueroAdmin)
admin.site.register(Wochentage, WochentageAdmin)
