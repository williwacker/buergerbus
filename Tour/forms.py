import logging
from datetime import datetime, time, timedelta

from django import forms
from django.conf import settings
from django.forms import BaseForm, ModelForm
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from jet.filters import RelatedFieldAjaxListFilter

from Basis.utils import append_br
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Einsatztage.models import Fahrtag
from Klienten.models import Klienten
from Tour.models import Tour

from .utils import DepartureTime, DistanceMatrix, GuestCount

logger = logging.getLogger(__name__)


class MyModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyModelForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['klient'].queryset = Klienten.objects.order_by('name').filter(typ='F')

    def update_conflict_direction(self, direction):
        if len(self.cleaned_data['konflikt_richtung']) == 0:
            self.cleaned_data['konflikt_richtung'] = direction
        else:
            if self.cleaned_data['konflikt_richtung'] != 'B' and self.cleaned_data['konflikt_richtung'] != direction:
                self.cleaned_data['konflikt_richtung'] = 'B'

    def clean(self):
        id = self.cleaned_data.get('id', 0)
        bus = self.cleaned_data.get('bus')
        datum = self.cleaned_data.get('datum')
        uhrzeit = self.cleaned_data.get('uhrzeit')
        zustieg = self.cleaned_data.get('zustieg')

        # will Team Konflikte bei der Eingabe ignorieren ?
        ignore_conflict_by_team = get_object_or_404(Bus, bus=bus).ignore_conflict

        # prüfe auf unique Tour Abfahrtszeit. Bei Zustieg addiere solange 1 sec bis die Uhrzeit unique ist
        instance = Tour.objects.filter(bus=bus, datum=datum, uhrzeit=uhrzeit).exclude(id__in=[id]).first()
        if instance:
            if zustieg:
                while instance:
                    uhrzeit = (datetime.combine(datetime(year=100, month=1, day=1),
                                                instance.uhrzeit) + timedelta(seconds=1)).time()
                    instance = Tour.objects.filter(bus=bus, datum=datum, uhrzeit=uhrzeit).exclude(id__in=[id]).first()
                self.cleaned_data['uhrzeit'] = uhrzeit
            else:
                raise forms.ValidationError('Tour zur gleicher Abholzeit ist bereits gebucht.')

        self.cleaned_data['konflikt'] = ''
        self.cleaned_data['konflikt_richtung'] = ''
        self.cleaned_data['konflikt_zeiten'] = ''

        logger.info('calculate time to destination')
        googleDict = DistanceMatrix().get_form_data(self.cleaned_data)
        if googleDict:
            self.cleaned_data['entfernung'] = googleDict['distance']
            self.cleaned_data['ankunft'] = googleDict['arrivaltime']
            self.instance.entfernung = googleDict['distance']
            self.instance.ankunft = googleDict['arrivaltime']
            self.changed_data.append('entfernung')
            self.changed_data.append('ankunft')

        earliest_departure_conflict = False

        # Kann der Fahrer pünktlich am Morgen oder aus der Pause starten?
        frueheste_abfahrt_1 = DepartureTime().check_tour_start(self.cleaned_data)
        if frueheste_abfahrt_1 > self.cleaned_data['uhrzeit']:
            tourstart = DepartureTime().get_timeslot_start(
                self.cleaned_data['bus'],
                self.cleaned_data['datum'].datum.isoweekday(),
                self.cleaned_data['uhrzeit'])
            earliest_departure_conflict = True
            self.update_conflict_direction('U')
            self.cleaned_data['konflikt'] = append_br(
                self.cleaned_data['konflikt'],
                "Tour Start um {} kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(
                    tourstart.strftime("%H:%M"),
                    frueheste_abfahrt_1.strftime("%H:%M")))

        # Kann der Bus zum gewünschten Zeitpunkt am Abholort sein ?
        frueheste_abfahrt_2 = DepartureTime().check_previous_client(self.cleaned_data)
        if frueheste_abfahrt_2 == time(0, 0, 0):
            self.cleaned_data['zustieg'] = False

        if frueheste_abfahrt_2 > self.cleaned_data['uhrzeit']:
            earliest_departure_conflict = True
            self.update_conflict_direction('U')
            self.cleaned_data['konflikt'] = append_br(
                self.cleaned_data['konflikt'],
                "Abfahrtszeit kann aufgrund der vorhergehenden Tour nicht eingehalten werden. Frühest mögliche Abfahrt um {}".
                format(frueheste_abfahrt_2.strftime("%H:%M")))

        if earliest_departure_conflict:
            self.cleaned_data['konflikt_zeiten'] += force_text('\n↑', encoding='utf-8', strings_only=False, errors='strict') + \
                max(frueheste_abfahrt_1, frueheste_abfahrt_2).strftime("%H:%M")

        latest_departure_conflict = False

        # Kann der Fahrer pünktlich Pause oder Feierabend machen?
        spaeteste_abfahrt_1 = DepartureTime().check_tour_end(self.cleaned_data)
        if spaeteste_abfahrt_1 < self.cleaned_data['uhrzeit']:
            tourende = Latest_DepartureTime().get_timeslot_end(
                self.cleaned_data['bus'],
                self.cleaned_data['datum'].datum.isoweekday(),
                self.cleaned_data['uhrzeit'])
            latest_departure_conflict = True
            self.update_conflict_direction('D')
            self.cleaned_data['konflikt'] = append_br(
                self.cleaned_data['konflikt'],
                "Tour Ende um {} kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(
                    tourende.strftime("%H:%M"),
                    spaeteste_abfahrt_1.strftime("%H:%M")))

        # Kann der Termin eingehalten werden?
        spaeteste_abfahrt_2 = DepartureTime().check_appointment(self.cleaned_data)
        if spaeteste_abfahrt_2 < self.cleaned_data['uhrzeit']:
            latest_departure_conflict = True
            self.update_conflict_direction('D')
            self.cleaned_data['konflikt'] = append_br(
                self.cleaned_data['konflikt'],
                "Termin um {} kann nicht eingehalten werden. Empfohlene Abfahrt vor {}".format(
                    self.cleaned_data['termin'].strftime("%H:%M"),
                    spaeteste_abfahrt_2.strftime("%H:%M")))

        # Kann der nächste Fahrgast zum geplanten Zeitpunkt abgeholt werden?
        spaeteste_abfahrt_3 = DepartureTime().check_next_client(self.cleaned_data)
        # Konflikt nur anzeigen falls Abfahrt noch früher erfolgen müsste
        if spaeteste_abfahrt_3 < self.cleaned_data['uhrzeit'] and spaeteste_abfahrt_3 < spaeteste_abfahrt_2:
            latest_departure_conflict = True
            self.update_conflict_direction('D')
            self.cleaned_data['konflikt'] = append_br(
                self.cleaned_data['konflikt'],
                "Abfahrtszeit des nächsten Fahrgastes kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(
                    spaeteste_abfahrt_3.strftime("%H:%M")))

        if latest_departure_conflict:
            self.cleaned_data['konflikt_zeiten'] += force_text('\n↓', encoding='utf-8', strings_only=False, errors='strict') + \
                min(spaeteste_abfahrt_1, spaeteste_abfahrt_2, spaeteste_abfahrt_3).strftime("%H:%M")

        # Sind genügend Plätze verfügbar ?
        bus = Bus.objects.get(bus=self.cleaned_data['bus'])
        if GuestCount().get(self.cleaned_data) > bus.sitzplaetze:
            if self.cleaned_data['zustieg']:
                raise forms.ValidationError(
                    "Maximale Anzahl Fahrgäste überschritten. Kein Zustieg möglich. Bitte Extrafahrt planen")
            else:
                raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Bitte Extrafahrt planen")

        self.instance.konflikt = self.cleaned_data['konflikt']
        self.instance.konflikt_richtung = self.cleaned_data['konflikt_richtung']
        self.instance.konflikt_zeiten = self.cleaned_data['konflikt_zeiten']
        if self.cleaned_data['konflikt'] and not self.cleaned_data['konflikt_ignorieren'] and not ignore_conflict_by_team:
            raise forms.ValidationError(self.cleaned_data['konflikt'])

        return self.cleaned_data


class TourAddForm1(forms.Form):
    fahrgast = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name').filter(typ='F'))


class TourAddForm2(MyModelForm):
    fahrgast = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Fahrgast')
    bus_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Bus')
    konflikt_ignorieren = forms.BooleanField(
        required=False, help_text="Tour erst mal speichern und zu einem späteren Zeitpunkt ändern.")

    class Meta:
        model = Tour
        fields = ['fahrgast', 'bus_2', 'klient', 'bus', 'datum', 'uhrzeit', 'zustieg', 'personenzahl',
                  'abholklient', 'zielklient', 'termin', 'bemerkung', 'konflikt_ignorieren']
        widgets = {
            'klient': forms.HiddenInput(),
            'bus': forms.HiddenInput(),
            'uhrzeit': forms.TimeInput(attrs={'class': 'vTimeField'}),
            'termin': forms.TimeInput(attrs={'class': 'vTimeField'}),
            'bemerkung': forms.Textarea(attrs={'rows': '5'}), }


class TourChgForm(MyModelForm):
    fahrgast = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Fahrgast')
    bus_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Bus')
    konflikt_ignorieren = forms.BooleanField(
        required=False, help_text="Tour erst mal speichern und zu einem späteren Zeitpunkt ändern.")
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Tour
        fields = ['id', 'fahrgast', 'bus_2', 'klient', 'bus', 'datum', 'uhrzeit', 'zustieg', 'personenzahl',
                  'abholklient', 'zielklient', 'entfernung', 'ankunft', 'termin', 'bemerkung', 'konflikt_ignorieren']
        widgets = {
            'klient': forms.HiddenInput(),
            'bus': forms.HiddenInput(),
            'entfernung': forms.HiddenInput(),
            'ankunft': forms.HiddenInput(),
            'uhrzeit': forms.TimeInput(attrs={'class': 'vTimeField'}),
            'termin': forms.TimeInput(attrs={'class': 'vTimeField'}),
            'bemerkung': forms.Textarea(attrs={'rows': '5'}), }

    def __init__(self, *args, **kwargs):
        super(TourChgForm, self).__init__(*args, **kwargs)
