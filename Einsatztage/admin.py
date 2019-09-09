from django.contrib import admin
from Einsatzmittel.utils import get_bus_list, get_buero_list

from Einsatztage.models import Fahrtag, Buerotag
from Einsatzmittel.models import Bus, Buero
from Team.models import Fahrer, Koordinator
from .utils import FahrtageSchreiben, BuerotageSchreiben


class FahrtagAdmin(admin.ModelAdmin):
	fields = ('datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'archiv' )
	search_fields = ('datum',)
	ordering = ('team', 'datum',)
#	list_display = ('datum', 'wochentag', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'klienten_anzahl')
	list_filter = ('team', 'archiv')
#    list_editable = ('fahrer_vormittag','fahrer_nachmittag')
	readonly_fields = ('archiv',)

	def get_form(self, request, obj=None, **kwargs):
		if request.user.is_superuser:
			self.fields = ['datum',  'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'archiv']
		else:
			self.fields = ['datum',  'team', 'fahrer_vormittag', 'fahrer_nachmittag']
		return super(FahrtagAdmin, self).get_form(request, obj=None, **kwargs)

	def changelist_view(self, request, extra_context=None):
		if request.user.is_superuser:
			self.list_display = ['datum', 'team', 'fahrer_vormittag', 'gaeste_vormittag', 'fahrer_nachmittag', 'gaeste_nachmittag', 'archiv']
		else:
			self.list_display = ['datum', 'team', 'fahrer_vormittag', 'gaeste_vormittag', 'fahrer_nachmittag', 'gaeste_nachmittag']
		return super(FahrtagAdmin, self).changelist_view(request, extra_context)

	def get_queryset(self, request):
		qs = super(FahrtagAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(archiv=False, team__in=get_bus_list(request))

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name in ["fahrer_vormittag", "fahrer_nachmittag"]:
			kwargs["queryset"] = Fahrer.objects.filter(aktiv=True)
		if db_field.name == "team":		
			kwargs["queryset"] = Bus.objects.filter(bus__in=get_bus_list(request))
			
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def save_model(self, request, obj, form, change):
		ETS = FahrtageSchreiben()
		ETS.archive_past_fahrtage()
		ETS.write_new_fahrtage(obj.datum)
		obj.user = request.user
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Fahrtag, FahrtagAdmin)

##############################
#######  Buero Admin part
##############################

class BuerotagAdmin(admin.ModelAdmin):
#    fields = ('datum', 'team', 'mitarbeiter', 'archiv' )
	search_fields = ('datum',)
	ordering = ('team', 'datum',)
#	list_display = ('datum', 'wochentag', 'team', 'mitarbeiter')
	list_filter = ('team',)
#    list_editable = ('mitarbeiter',)
	readonly_fields = ('archiv',)

	def get_form(self, request, obj=None, **kwargs):
		if request.user.is_superuser:
			self.fields = ['datum', 'wochentag', 'team', 'mitarbeiter', 'archiv']
		else:
			self.fields = ['datum', 'wochentag', 'team', 'mitarbeiter']
		return super(BuerotagAdmin, self).get_form(request, obj=None, **kwargs)

	def changelist_view(self, request, extra_context=None):
		if request.user.is_superuser:
			self.list_display = ['datum', 'wochentag', 'team', 'mitarbeiter', 'archiv']
		else:
			self.list_display = ['datum', 'wochentag', 'team', 'mitarbeiter']
		return super(BuerotagAdmin, self).changelist_view(request, extra_context)

	def get_queryset(self, request):
		qs = super(BuerotagAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(archiv=False, team__in=get_buero_list(request))

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "mitarbeiter":
			kwargs["queryset"] = Koordinator.objects.filter(aktiv=True)
		if db_field.name == "team":		
			kwargs["queryset"] = Buero.objects.filter(id__in=get_buero_list(request))			
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def save_model(self, request, obj, form, change):
		ETS = BuerotageSchreiben()
		ETS.archive_past_buerotage()
		ETS.write_new_buerotage(obj.datum)
		obj.user = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Buerotag, BuerotagAdmin)
