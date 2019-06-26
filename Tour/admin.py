from django.contrib import admin

from Klienten.models import Klienten
from .models import Tour

class KlientenInline(admin.TabularInline):
	model = Klienten
	fk_name = "klient"


class TourAdmin(admin.ModelAdmin):
	list_display = ('bus', 'klient', 'uhrzeit')
	autocomplete_fields = ('klient',)

admin.site.register(Tour, TourAdmin)
