from django.contrib import admin

from .models import Klienten, Orte, Strassen

class KlientenAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	autocomplete_fields = ('strasse',)
	ordering = ('name',)
	list_filter = ('ort',)
	list_display = ('name', 'telefon', 'ort', 'strasse', 'hausnr' )
	fieldsets = (
		('Stammdaten', { 'fields': ('name', 'telefon', 'mobil')}),
		('Adresse', {'fields': ('ort', 'strasse', 'hausnr')})
)
class OrteAdmin(admin.ModelAdmin):
	list_display = ('ort','bus')
	ordering = ('ort',)

class StrassenAdmin(admin.ModelAdmin):
	list_display = ('ort', 'strasse')
	ordering = ('ort','strasse')
	list_filter = ('ort',)
	search_fields = ('strasse', 'ort__ort')

admin.site.register(Klienten, KlientenAdmin)
admin.site.register(Orte, OrteAdmin)
admin.site.register(Strassen, StrassenAdmin)