import logging
from datetime import datetime, time, timedelta

from django import forms
from django.conf import settings
from django.forms import BaseForm, ModelForm
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from jet.filters import RelatedFieldAjaxListFilter

from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Einsatztage.models import Fahrtag
from Klienten.models import Klienten
from Tour.models import Tour

from .utils import (DepartureTime, DistanceMatrix, GuestCount,
                    Latest_DepartureTime)

logger = logging.getLogger(__name__)

class MyModelForm(ModelForm):
	def __init__(self,*args,**kwargs):
		super (MyModelForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['klient'].queryset = Klienten.objects.order_by('name').filter(typ='F')

	def clean(self):
		self.cleaned_data['konflikt'] = ''
		self.cleaned_data['konflikt_richtung'] = ''		

		# Sind genügend Plätze verfügbar ?
		bus = Bus.objects.get(bus=self.cleaned_data['bus'])
		if GuestCount().get(self) > bus.sitzplaetze:
			if self.cleaned_data['zustieg']:
				raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Kein Zustieg möglich. Bitte Extrafahrt planen")
			else:
				raise forms.ValidationError("Maximale Anzahl Fahrgäste überschritten. Bitte Extrafahrt planen")

		# Kann der Bus zum gewünschten Zeitpunkt am Anholort sein ?
		frueheste_abfahrt = DepartureTime().time(self)
		if frueheste_abfahrt == time(0,0,0):
			self.cleaned_data['zustieg'] = False
		if frueheste_abfahrt > self.cleaned_data['uhrzeit']:
			self.cleaned_data['konflikt'] += "Abfahrtszeit kann nicht eingehalten werden. Frühest mögliche Abfahrt um {}".format(str(frueheste_abfahrt))
			self.cleaned_data['konflikt_richtung'] += force_text('↑', encoding='utf-8', strings_only=False, errors='strict')
			if not self.cleaned_data['konflikt_ignorieren']:	
				raise forms.ValidationError(self.cleaned_data['konflikt'])

		# Kann der nächste Fahrgast zum geplanten Zeitpunkt abgeholt werden?
		spaeteste_abfahrt = Latest_DepartureTime().time(self)
		if spaeteste_abfahrt != time(0,0,0) and spaeteste_abfahrt < self.cleaned_data['uhrzeit']:
			self.cleaned_data['konflikt'] += "<br>" if len(self.cleaned_data['konflikt']) > 0 else ''
			self.cleaned_data['konflikt'] += "Abfahrtszeit des nächsten Fahrgastes kann nicht eingehalten werden. Empfohlene Abfahrt um {}".format(str(spaeteste_abfahrt))
			self.cleaned_data['konflikt_richtung'] += force_text('↓', encoding='utf-8', strings_only=False, errors='strict')
			if not self.cleaned_data['konflikt_ignorieren']:
				raise forms.ValidationError(self.cleaned_data['konflikt'])

		self.instance.konflikt 			= self.cleaned_data['konflikt']
		self.instance.konflikt_richtung = self.cleaned_data['konflikt_richtung']
		return self.cleaned_data

class TourAddForm1(forms.Form):
	fahrgast  = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name').filter(typ='F'))

class TourAddForm2(MyModelForm):
	fahrgast = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Fahrgast')
	bus_2    = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Bus')
	abholfavorit = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'), required=False, label="Wo",
		help_text="Bei wem soll der Fahrgast abgeholt werden? Wählen Sie links aus den vergangenen Touren aus oder rechts der gesamten Liste.")
	zielfavorit = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'), required=False, label="Wohin",
		help_text="Zu wem soll der Fahrgast gebracht werden? Wählen Sie links aus den vergangenen Touren aus oder rechts der gesamten Liste.")
	konflikt_ignorieren = forms.BooleanField(required=False,
		help_text="Tour erst mal speichern und zu einem späteren Zeitpunkt ändern.")

	class Meta:
		model = Tour
		fields = ['fahrgast','bus_2','klient','bus','datum','uhrzeit','zustieg','personenzahl',
					'abholfavorit','abholklient','zielfavorit','zielklient','bemerkung','konflikt_ignorieren']
		widgets = {'klient': forms.HiddenInput(), 'bus': forms.HiddenInput(),
				   'uhrzeit': forms.TimeInput(attrs={'class':'vTimeField'}), 'bemerkung': forms.Textarea(attrs={'rows':'5'}),
				  }

class TourChgForm(MyModelForm):
	fahrgast = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Fahrgast')
	bus_2    = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Bus')
	abholfavorit = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'), required=False, label="Wo",
		help_text="Bei wem soll der Fahrgast abgeholt werden? Wählen Sie links aus den vergangenen Touren aus oder rechts der gesamten Liste.")
	zielfavorit  = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'), required=False, label="Wohin",
		help_text="Zu wem soll der Fahrgast gebracht werden? Wählen Sie links aus den vergangenen Touren aus oder rechts der gesamten Liste.")
	konflikt_ignorieren = forms.BooleanField(required=False,
		help_text="Tour erst mal speichern und zu einem späteren Zeitpunkt ändern.")
	id		 = forms.IntegerField(required=False, widget=forms.HiddenInput())
	
	class Meta:
		model = Tour
		fields = ['id','fahrgast','bus_2','klient','bus','datum','uhrzeit','zustieg','personenzahl','abholfavorit','abholklient','zielfavorit','zielklient','entfernung','ankunft','bemerkung','konflikt_ignorieren']
		widgets = {'klient': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'entfernung': forms.HiddenInput(), 'ankunft': forms.HiddenInput(),
				   'uhrzeit': forms.TimeInput(attrs={'class':'vTimeField'}), 'bemerkung': forms.Textarea(attrs={'rows':'5'}),
				  }

	def __init__(self, *args, **kwargs):
		super(TourChgForm, self).__init__(*args, **kwargs)
