from django.contrib import admin
from jet.filters import RelatedFieldAjaxListFilter

from .models import Klienten, Orte, Strassen

class KlientenAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	ordering = ('name',)
	list_display = ('name', 'telefon', 'ort', 'strasse', 'hausnr' )
	list_editable = ('telefon','ort','strasse','hausnr')
	list_display_links = ('name',)
	fieldsets = (
		('Stammdaten', { 'fields': ('name', 'telefon', 'mobil')}),
		('Adresse', {'fields': ('ort', 'strasse', 'hausnr')}),
		('Weitere Info', {'fields': ('dsgvo', 'bemerkung')})
)
class OrteAdmin(admin.ModelAdmin):
	list_display = ('ort','bus')
	ordering = ('ort',)
	readonly_fields = ('bus',)

class StrassenAdmin(admin.ModelAdmin):
	list_display = ('ort', 'strasse')
	ordering = ('ort','strasse')
	list_filter = ('ort',)
	search_fields = ('strasse', 'ort__ort')

admin.site.register(Klienten, KlientenAdmin)
admin.site.register(Orte, OrteAdmin)
admin.site.register(Strassen, StrassenAdmin)