from django.forms import ModelForm, modelformset_factory
from django.shortcuts import render
from .models import Fahrtag, Buerotag

def manage_fahrer(request):
	FahrerFormSet = modelformset_factory(Fahrtag, fields=('datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag'))
	if request.method == 'POST':
		formset = FahrerFormSet(request.POST, request.FILES)
		if formset.is_valid():
			formset.save()
		else:
			formset = FahrerFormSet()
		return render(request, 'Einsatztage/detail.html', {'formset':formset})



class FahrtagAddForm(ModelForm):
	class Meta:
		model = Fahrtag
		fields = ['datum', 'team', 'fahrer_vormittag', 'fahrer_nachmittag']

		form = FahrtagAddForm()

