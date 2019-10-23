from datetime import datetime, timedelta, time
from django import forms
from django.conf import settings
from django.forms import ModelForm, modelformset_factory
from jet.filters import RelatedFieldAjaxListFilter
from django.utils.translation import ugettext_lazy as _

from Tour.models import Tour
from .utils import DistanceMatrix, DepartureTime, JoinTime, GuestCount
from Klienten.models import Klienten
from Einsatzmittel.models import Bus
from Einsatztage.models import Fahrtag
from Einsatzmittel.utils import get_bus_list

class MyModelForm(ModelForm):
	def __init__(self,*args,**kwargs):
		super (MyModelForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['klient'].queryset = Klienten.objects.order_by('name').filter(typ='F')

class TourenForm(MyModelForm):
	class Meta:
		model = Tour
		fields = ['klient','bus','datum','uhrzeit','entfernung','ankunft']

class TourAddForm1(forms.Form):
	fahrgast  = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name').filter(typ='F'))


class TourAddForm2(forms.Form):
	klient = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Fahrgast')
	bus = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}))
	datum = forms.ModelChoiceField(queryset=Fahrtag.objects.order_by('datum').filter(archiv=False, datum__gt=datetime.now()), empty_label=None)
	uhrzeit = forms.TimeField(widget=forms.TimeInput(attrs={'class':'vTimeField'}))
	zustieg = forms.BooleanField(required=False, label='Zustieg zu vorherigem Fahrgast')
	personenzahl = forms.IntegerField(initial=1, min_value=1, label='Anzahl Personen')
	abholklient = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'), help_text="Bei wem soll der Fahrgast abgeholt werden?")
	zielklient = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'), help_text="Zu wem soll der Fahrgast gebracht werden?")
	bemerkung = forms.CharField(max_length=200, required=False, widget=forms.Textarea)

	def clean(self):
		if self.cleaned_data['zustieg']:
			frueheste_abfahrt = JoinTime().time(self.cleaned_data)
		else:
			frueheste_abfahrt = DepartureTime().time(self.cleaned_data)
		if frueheste_abfahrt == time(0,0,0):
			self.cleaned_data['zustieg'] = False
		if self.cleaned_data['zustieg'] and frueheste_abfahrt > self.cleaned_data['uhrzeit']:
			raise forms.ValidationError("Abfahrtszeit kann nicht eingehalten werden. Frühest mögliche Abfahrt um {}".format(str(frueheste_abfahrt)))

		bus = Bus.objects.get(bus=self.cleaned_data['bus'])
		if GuestCount().get(self.cleaned_data) > bus.sitzplaetze:
			if self.cleaned_data['zustieg']:  # fahrgäste wollen zusteigen
				raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Kein Zustieg möglich. Bitte Extrafahrt planen")
			else:
				raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Bitte Extrafahrt planen")
		
class TourChgForm(TourenForm):
	fahrgast = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Fahrgast')
	bus_2    = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Bus')

	class Meta:
		model = Tour
		fields = ['fahrgast','bus_2','klient','bus','datum','uhrzeit','zustieg','personenzahl','abholklient','zielklient','entfernung','ankunft','bemerkung']
		widgets = {'klient': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'entfernung': forms.HiddenInput(), 'ankunft': forms.HiddenInput(),
				   'uhrzeit': forms.TimeInput(attrs={'class':'vTimeField'})}

	def clean(self):
		if self.cleaned_data['zustieg']:
			frueheste_abfahrt = JoinTime().time(self.cleaned_data)
		else:
			frueheste_abfahrt = DepartureTime().time(self.cleaned_data)
		if frueheste_abfahrt == time(0,0,0):
			self.cleaned_data['zustieg'] = False
		if self.cleaned_data['zustieg'] and frueheste_abfahrt > self.cleaned_data['uhrzeit']:
			raise forms.ValidationError("Abfahrtszeit kann nicht eingehalten werden. Frühest mögliche Abfahrt um {}".format(str(frueheste_abfahrt)))

		bus = Bus.objects.get(bus=self.cleaned_data['bus'])
		if GuestCount().get(self.cleaned_data) > bus.sitzplaetze:
			if self.cleaned_data['zustieg']:  # fahrgäste wollen zusteigen
				raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Kein Zustieg möglich. Bitte Extrafahrt planen")
			else:
				raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Bitte Extrafahrt planen")