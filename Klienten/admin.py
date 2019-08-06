from django.contrib import admin
from jet.filters import RelatedFieldAjaxListFilter

from .models import Klienten, Orte, Strassen, KlientenBus
from Einsatzmittel.models import Bus

class KlientenAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	ordering = ('name',)
	list_display = ('name', 'telefon', 'ort', 'strasse', 'hausnr', 'bus' )
	list_filter = ('name','ort')
#	list_editable = ('telefon','ort','strasse','hausnr')
	list_display_links = ('name',)
	fieldsets = (
		('Stammdaten', { 'fields': ('name', 'telefon', 'mobil')}),
		('Adresse', {'fields': ('ort', 'strasse', 'hausnr')}),
		('Weitere Info', {'fields': ('dsgvo', 'bemerkung', 'bus')})
	)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "bus":
			kwargs["queryset"] = Bus.objects.filter(wird_verwaltet=True)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def get_readonly_fields(self, request, obj=None):
		if obj:
			return []
		else:
			return ["bus"]

	def save_model(self, request, obj, form, change):
		# Bus nach Klientenort setzen
		if (obj.bus is None):
			obj.bus = obj.ort.bus
		obj.user = request.user
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)

		if (KlientenBus.objects.filter(name_id=obj.id).count() == 0):
			b = KlientenBus(name=obj, bus=obj.bus)
			b.save()
		else:
			KlientenBus.objects.filter(name_id=obj.id).update(bus=obj.bus)
		


class KlientenBusAdmin(admin.ModelAdmin):
	list_display = ('name','bus')
	ordering = ('name',)
#	readonly_fields = ('bus',)

class OrteAdmin(admin.ModelAdmin):
	list_display = ('ort','bus')
	ordering = ('ort',)
	readonly_fields = ('bus',)	

class StrassenAdmin(admin.ModelAdmin):
	list_display = ('ort', 'strasse')
	ordering = ('ort','strasse')
	list_filter = ('ort',)
	search_fields = ('strasse', 'ort__ort')

	def get_readonly_fields(self, request, obj=None):
		if obj:
			return ["ort"]
		else:
			return []

admin.site.register(Klienten, KlientenAdmin)
admin.site.register(KlientenBus, KlientenBusAdmin)
admin.site.register(Orte, OrteAdmin)
admin.site.register(Strassen, StrassenAdmin)