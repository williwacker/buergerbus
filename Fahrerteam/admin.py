from django.contrib import admin

from .models import Fahrer

class FahrerAdmin(admin.ModelAdmin):
#	def abholort(self, obj):
#		return ', '.join([obj.abholklient.ort.ort, obj.abholklient.strasse.strasse +" "+obj.abholklient.hausnr])
	
    list_display = ('name', 'team', 'email', 'mobil', 'aktiv')
    list_filter = ('team',)
    list_editable = ('email','mobil')
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super(FahrerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(aktiv=True)

admin.site.register(Fahrer, FahrerAdmin)
