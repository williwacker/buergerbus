from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Fahrtag

def index(request):
	einsatz_liste = Einsatztag.objects.order_by('datum')
	context = {'einsatz_liste':einsatz_liste}
	return render(request, 'Einsatztage/index.html', context)

def detail(request, id):
    details = get_object_or_404(Einsatztag, pk=id)
    context = {'details':details}
    print(details)
    return render(request, 'Einsatztage/detail.html', context)

def results(request, id):
	response = "You're looking at the results of Einsatztage %s."
	return HttpResponse(response % name_id)