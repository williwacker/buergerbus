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

#class MyModelForm(ModelForm):
#	def __init__(self,*args,**kwargs):
#		super (MyModelForm,self ).__init__(*args,**kwargs) # populates the post
#		self.fields['ort'].queryset = Orte.objects.order_by('ort').filter(bus__in=get_bus_list(kwargs['request']))
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

class FahrgastAddForm(KlientenForm):

	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','bemerkung','dsgvo','bus','typ']
		widgets = {'dsgvo': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'typ': forms.HiddenInput()}

class FahrgastChgForm(KlientenForm):
		
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','bemerkung','dsgvo','bus','typ']
		widgets = {'dsgvo': forms.Select(choices=DSGVO_AUSWAHL), 'typ': forms.HiddenInput()}	

class DienstleisterChgForm(ModelForm):
		
	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','bemerkung','dsgvo','bus','typ']
		widgets = {'dsgvo': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'typ': forms.HiddenInput()}		

class DienstleisterAddForm(ModelForm):

	class Meta:
		model = Klienten
		fields = ['name','telefon','mobil','ort','strasse','hausnr','bemerkung','dsgvo','bus','typ']
		widgets = {'dsgvo': forms.HiddenInput(), 'bus': forms.HiddenInput(), 'typ': forms.HiddenInput()}

class OrtAddForm(ModelForm):

	class Meta:
		model = Orte
		fields = ['ort','bus']
		