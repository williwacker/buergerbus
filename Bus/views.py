from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Bus

def index(request):
	bus_liste = Bus.objects.order_by('bus_id')
	context = {'bus_liste':bus_liste}
	return render(request, 'Bus/index.html', context)

def detail(request, bus_id):
    details = get_object_or_404(Bus, pk=bus_id)
    context = {'details':details}
    print(details)
    return render(request, 'Bus/detail.html', context)

def results(request, bus_id):
	response = "You're looking at the results of bus %s."
	return HttpResponse(response % bus_id)