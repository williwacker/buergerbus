from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.forms import ModelForm, modelformset_factory
from django.utils.translation import ugettext_lazy as _
from jet.filters import RelatedFieldAjaxListFilter

from Einsatzmittel.utils import get_bus_list

from .models import DSGVO_AUSWAHL, Klienten, Orte, Strassen
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
		if data: data = data.replace('/','-')
		return data

	def clean_mobil(self):
		data = self.cleaned_data['mobil']
		if data: data = data.replace('/','-')
		return data

class KlientenSearchForm(forms.Form):
	suchname = forms.CharField(required=True, label='Suchbegriff', help_text='z.B. Name, Gewerbe oder Telefonnummer')
	suchort  = forms.CharField(required=True, label='Ort')

class KlientenSearchResultForm(forms.Form):
	suchergebnis = forms.ChoiceField(required=False, widget=forms.RadioSelect())
	city_create  = forms.BooleanField(required=False, label="Ort und Strasse anlegen", 
					help_text="Neuen Ort und/oder Strasse anlegen")
	force_create = forms.BooleanField(required=False, label="Ähnlichkeit erlauben", 
					help_text="Dienstleister anlegen, obwohl schon ein Eintrag mit ähnlichem Namen existiert")

	def clean_suchergebnis(self):
		data = self.cleaned_data['suchergebnis']
		if not data: raise forms.ValidationError("Bitte erst einen Eintrag aus der Liste wählen")
		return data	

class DienstleisterForm(ModelForm):

	def clean_telefon(self):
		data = self.cleaned_data['telefon']
		if data: data = data.replace('/','-')
		return data

	def clean_mobil(self):
		data = self.cleaned_data['mobil']
		if data: data = data.replace('/','-')
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
		fields = ['name','telefon','mobil','ort','strasse','hausnr','kategorie','bemerkung','typ']
		widgets = {'bemerkung': forms.Textarea(attrs={'rows':'5'}),'typ': forms.HiddenInput()}

class DienstleisterChgForm(DienstleisterForm):	
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','kategorie','bemerkung']
		widgets = {'bemerkung': forms.Textarea(attrs={'rows':'5'})}

class OrtAddForm(ModelForm):
	class Meta:
		model = Orte
		fields = ['ort','plz','bus']

class OrtChgForm(ModelForm):
	class Meta:
		model = Orte
		fields = ['ort','plz','bus']

	def __init__(self, *args, **kwargs):
		super(OrtChgForm, self).__init__(*args, **kwargs)
		self.fields['ort'].disabled = True
		self.fields['ort'].required = False			

class StrassenForm(ModelForm):
	class Meta:
		model = Strassen
		fields = ['ort','strasse']	

class StrassenAddForm(ModelForm):	
	class Meta:
		model = Strassen
		fields = ['ort','strasse']	

class StrassenChgForm(ModelForm):
	
	class Meta:
		model = Strassen
		fields = ['ort','strasse']

	def __init__(self, *args, **kwargs):
		super(StrassenChgForm, self).__init__(*args, **kwargs)
		self.fields['ort'].disabled = True
		self.fields['ort'].required = False			
