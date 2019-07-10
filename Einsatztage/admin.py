from django.contrib import admin
from berechnung_feiertage import Holidays
import datetime, time

from Einsatztage.models import Fahrtag, Buerotag
from Einsatzmittel.models import Bus, Buero
from Team.models import Fahrer, Buerokraft

class FahrtageSchreiben():

    def read_bus_tage(self):
        bus_dict = {}
        rows = Bus.objects.filter(wird_verwaltet=True).values_list('bus', flat=True)
        managed_busses = [row for row in rows]

        tage_liste = ['So','Mo','Di','Mi','Do','Fr']
        for bus in managed_busses:
            tage_nr = []
            rows = Bus.objects.filter(bus=bus).values_list('fahrtage', flat=True)
            fahrtage = [row for row in rows]
            if (fahrtage):
                for tag in fahrtage[0].split(","):
                    for i in range(len(tage_liste)):
                        if tag in tage_liste[i]:
                            tage_nr.append(i)
                bus_dict[bus] = tage_nr
        return(bus_dict)    

    def write_new_fahrtage(self,changedate):
        # die nächsten Feiertage ausrechnen
        holiday_list = []
        holidays = Holidays(int(time.strftime("%Y")), 'RP')
        for holiday in holidays.get_holiday_list():
            holiday_list.append(holiday[0])
        holidays = Holidays(int(time.strftime("%Y"))+1, 'RP')
        for holiday in holidays.get_holiday_list():
            holiday_list.append(holiday[0])

        bus_tage = self.read_bus_tage()
        for bus_id in bus_tage:
            b = Bus.objects.get(pk=int(bus_id))
            rows = Fahrtag.objects.filter(team=b, archiv=False).values_list('datum',flat=True)
            existierende_tage = [row for row in rows]

            # die Fahrtage für die nächsten 30 Tage ausrechnen
            for i in range(1,30):
                neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
                if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
                    if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
                        if neuer_tag.weekday() in bus_tage[bus_id]:   # Tag ist ein Fahrtag
                            if changedate != neuer_tag:
                                t = Fahrtag(datum=neuer_tag, team=b)
                                t.save()

    def archive_past_fahrtage(self):
        rows = Fahrtag.objects.filter(archiv=False).values_list('datum','id')
        existierende_tage = [row for row in rows]
        for tag, id in existierende_tage:
            if tag <= datetime.date.today():
                t = Fahrtag.objects.get(pk=id)
                t.archiv=True
                t.save()

class FahrtagAdmin(admin.ModelAdmin):
    fields = ('datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'archiv' )
    search_fields = ('datum',)
    ordering = ('team', 'datum',)
    list_display = ('datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag', 'archiv' )
    list_filter = ('team',)
    list_editable = ('fahrer_vormittag','fahrer_nachmittag')

    def get_queryset(self, request):
        qs = super(FahrtagAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(archiv=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["fahrer_vormittag", "fahrer_nachmittag"]:
            kwargs["queryset"] = Fahrer.objects.filter(aktiv=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        ETS = FahrtageSchreiben()
        ETS.archive_past_fahrtage()
        ETS.write_new_fahrtage(obj.datum)
        obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Fahrtag, FahrtagAdmin)

##############################
#######  Buero Admin part
##############################

class BuerotageSchreiben():

    def read_buero_tage(self):
        buero_dict = {}
        rows = Buero.objects.filter(wird_verwaltet=True).values_list('id', flat=True)
        managed_bueros = [row for row in rows]

        tage_liste = ['So','Mo','Di','Mi','Do','Fr']
        for id in managed_bueros:
            tage_nr = []
            rows = Buero.objects.filter(id=id).values_list('buerotage', flat=True)
            buerotage = [row for row in rows]
            if (buerotage):
                for tag in buerotage[0].split(","):
                    for i in range(len(tage_liste)):
                        if tag in tage_liste[i]:
                            tage_nr.append(i)
                buero_dict[id] = tage_nr
        return(buero_dict)    

    def write_new_buerotage(self,changedate):
        # die nächsten Feiertage ausrechnen
        holiday_list = []
        holidays = Holidays(int(time.strftime("%Y")), 'RP')
        for holiday in holidays.get_holiday_list():
            holiday_list.append(holiday[0])
        holidays = Holidays(int(time.strftime("%Y"))+1, 'RP')
        for holiday in holidays.get_holiday_list():
            holiday_list.append(holiday[0])

        buero_tage = self.read_buero_tage()
        for id in buero_tage:
            b = Buero.objects.get(pk=id)
            rows = Buerotag.objects.filter(team=b, archiv=False).values_list('datum',flat=True)
            existierende_tage = [row for row in rows]

            # die Bürotage für die nächsten 30 Tage ausrechnen
            for i in range(1,30):
                neuer_tag = datetime.date.today() + datetime.timedelta(days=i)
                if neuer_tag not in existierende_tage:  # Tag ist nicht bereits definiert
                    if neuer_tag not in holiday_list:   # Tag ist kein Feiertag
                        if neuer_tag.weekday() in buero_tage[id]:   # Tag ist ein Bürotag
                            if changedate != neuer_tag:
                                t = Buerotag(datum=neuer_tag, team=b)
                                t.save()

    def archive_past_buerotage(self):
        rows = Buerotag.objects.filter(archiv=False).values_list('datum','id')
        existierende_tage = [row for row in rows]
        for tag, id in existierende_tage:
            if tag < datetime.date.today():
                t = Buerotag.objects.get(pk=id)
                t.archiv=True
                t.save()

class BuerotagAdmin(admin.ModelAdmin):
    fields = ('datum', 'team', 'mitarbeiter', 'archiv' )
    search_fields = ('datum',)
    ordering = ('team', 'datum',)
    list_display = ('datum', 'team', 'mitarbeiter', 'archiv' )
    list_filter = ('team',)
    list_editable = ('mitarbeiter',)

    def get_queryset(self, request):
        qs = super(BuerotagAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(archiv=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mitarbieter":
            kwargs["queryset"] = Buerokraft.objects.filter(aktiv=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        ETS = BuerotageSchreiben()
        ETS.archive_past_buerotage()
        ETS.write_new_buerotage(obj.datum)
        obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Buerotag, BuerotagAdmin)
