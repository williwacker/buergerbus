from django.contrib import admin

from .models import Bus

#class BusAdmin(admin.ModelAdmin):
#	search_fields = ('datum',)
#	autocomplete_fields = ('datum',)
#	ordering = ('datum',)
#	list_display = ('datum', 'fahrer_vormittag', 'fahrer_nachmittag' )

admin.site.register(Bus)

