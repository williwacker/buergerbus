from datetime import datetime, timedelta, time
from django import forms
from django.forms import ModelForm, modelformset_factory
from jet.filters import RelatedFieldAjaxListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Tour
from .utils import DistanceMatrix, DepartureTime
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
	fahrt_verbinden = forms.BooleanField(required=False)
	abholklient = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'))
	zielklient = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'))
	bemerkung = forms.CharField(max_length=200, required=False, widget=forms.Textarea)

	def clean(self):
		frueheste_abfahrt = DepartureTime().time(self.cleaned_data)
		if frueheste_abfahrt != time(0,0,0) and frueheste_abfahrt > self.cleaned_data['uhrzeit']:
			raise forms.ValidationError("Abfahrtszeit kann nicht eingehalten werden. Frühest mögliche Abfahrt um {}".format(str(frueheste_abfahrt)))
		
class TourChgForm(TourenForm):
	fahrgast = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Fahrgast')
	bus_2    = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Bus')

	class Meta:
		model = Tour
		fields = ['fahrgast','bus_2','klient','bus','datum','uhrzeit','abholklient','zielklient','entfernung','ankunft','bemerkung']
		widgets = {'klient': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'entfernung': forms.HiddenInput(), 'ankunft': forms.HiddenInput()}

	def clean(self):
		frueheste_abfahrt = DepartureTime().time(self.cleaned_data)
		if frueheste_abfahrt != time(0,0,0) and frueheste_abfahrt > self.cleaned_data['uhrzeit']:
			raise forms.ValidationError("Abfahrtszeit kann nicht eingehalten werden. Frühest mögliche Abfahrt um {}".format(str(frueheste_abfahrt)))