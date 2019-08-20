#from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django import forms
from django.forms import ModelForm, modelformset_factory
from jet.filters import RelatedFieldAjaxListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Tour
from Klienten.models import Klienten
from Einsatzmittel.models import Bus
from Einsatztage.models import Fahrtag
from Einsatzmittel.utils import get_bus_list
#from .sites import my_admin_site

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
	datum = forms.ModelChoiceField(queryset=Fahrtag.objects.order_by('datum').filter(archiv=False), empty_label=None)
	uhrzeit = forms.TimeField(widget=forms.TimeInput(attrs={'class':'vTimeField'}))
	abholklient = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'))
	zielklient = forms.ModelChoiceField(queryset=Klienten.objects.order_by('name'))
	bemerkung = forms.CharField(max_length=200, required=False, widget=forms.Textarea)
	

class TourChgForm(TourenForm):
	class Meta:
		model = Tour
		fields = ['klient','bus','datum','uhrzeit','abholklient','zielklient','entfernung','ankunft']
		widgets = {'entfernung': forms.HiddenInput(), 'ankunft': forms.HiddenInput()}

	def __init__(self, *args, **kwargs):
		super(TourChgForm, self).__init__(*args, **kwargs)       
		instance = getattr(self, 'instance', None)

		# When in EDIT mode.
		if instance and instance.id:
			self.fields['klient'].widget.attrs['disabled'] = 'True'
			self.fields['klient'].required = 'False'
			self.fields['bus'].widget.attrs['disabled'] = 'True'
			self.fields['bus'].required = 'False'			
