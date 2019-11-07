from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django import forms
from django.forms import ModelForm, modelformset_factory
from jet.filters import RelatedFieldAjaxListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Klienten, Orte, Strassen, DSGVO_AUSWAHL
from Einsatzmittel.utils import get_bus_list
from .sites import my_admin_site

StammdatenFormSet = modelformset_factory(Klienten, fields=('name','telefon','mobil'))
AdressFormSet = modelformset_factory(Klienten, fields=('ort','hausnr'))
InfoFormSet = modelformset_factory(Klienten, fields=('bemerkung',))

class KlientenForm(ModelForm):

	def clean_name(self):
		data = self.cleaned_data['name']
		try:
			n,v = data.split(', ')
		except:
			raise forms.ValidationError("Ungültiges Format")
		# Always return a value to use as the new cleaned data, even if
		# this method didn't change it.
		return data

	def clean_telefon(self):
		data = self.cleaned_data['telefon']
		if data:
			data = data.replace('/','-')
		return data

	def clean_mobil(self):
		data = self.cleaned_data['mobil']
		if data:
			data = data.replace('/','-')
		return data
TYP_AUSWAHL = [
	('F', 'Fahrgast'),
	('D', 'Dienstleister')
]

class KlientenSearchForm(forms.Form):
	name = forms.CharField(required=False, help_text='Name oder Telefonnummer')
	ort  = forms.ModelChoiceField(queryset=Orte.objects.order_by('ort'))
	typ  = forms.MultipleChoiceField(choices=TYP_AUSWAHL, required=False)

class KlientenSearchResultForm(forms.Form):
	suchergebnis = forms.CharField()
	details      = forms.CharField(required=False)
	widgets = {'details': forms.HiddenInput(),}

class DienstleisterForm(ModelForm):

	def clean_telefon(self):
		data = self.cleaned_data['telefon']
		if data:
			data = data.replace('/','-')
		return data

	def clean_mobil(self):
		data = self.cleaned_data['mobil']
		if data:
			data = data.replace('/','-')
		return data				

class FahrgastAddForm(KlientenForm):
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','bemerkung','dsgvo','bus','typ']
		widgets = {'dsgvo': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'typ': forms.HiddenInput(), 'bemerkung': forms.Textarea(attrs={'rows':'5'})}

class FahrgastChgForm(KlientenForm):
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','bemerkung','dsgvo','bus']
		widgets = {'bemerkung': forms.Textarea(attrs={'rows':'5'})}

class DienstleisterAddForm(DienstleisterForm):
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','kategorie','bemerkung']
		widgets = {'bemerkung': forms.Textarea(attrs={'rows':'5'})}

class DienstleisterChgForm(DienstleisterForm):	
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','kategorie','bemerkung']
		widgets = {'bemerkung': forms.Textarea(attrs={'rows':'5'})}

class OrtAddForm(ModelForm):
	class Meta:
		model = Orte
		fields = ['ort','bus']

class OrtChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(OrtChgForm, self).__init__(*args, **kwargs)
		self.fields['ort'].disabled = True
		self.fields['ort'].required = False	

	class Meta:
		model = Orte
		fields = ['ort','bus']		

class StrassenForm(ModelForm):
	class Meta:
		model = Strassen
		fields = ['ort','strasse']	

class StrassenAddForm(ModelForm):	
	class Meta:
		model = Strassen
		fields = ['ort','strasse']	

class StrassenChgForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(StrassenChgForm, self).__init__(*args, **kwargs)
		self.fields['ort'].disabled = True
		self.fields['ort'].required = False		
	class Meta:
		model = Strassen
		fields = ['ort','strasse']	