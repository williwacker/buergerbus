from django.contrib import admin

from .models import Einsatztag

class EinsatztagAdmin(admin.ModelAdmin):
    search_fields = ('datum',)
    ordering = ('datum',)
    list_display = ('datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag' )
    list_filter = ('team',)

#class EinsatztageFuellen():
#    for (i=0):
#        a = True

admin.site.register(Einsatztag, EinsatztagAdmin)
