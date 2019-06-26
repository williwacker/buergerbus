from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Klienten

def index(request):
	klienten_liste = Klienten.objects.order_by('id')
	context = {'klienten_liste':klienten_liste}
	return render(request, 'Klienten/index.html', context)

def detail(request, id):
    details = get_object_or_404(Bus, pk=id)
    context = {'details':details}
    print(details)
    return render(request, 'Klienten/detail.html', context)

def results(request, id):
	response = "You're looking at the results of klient %s."
	return HttpResponse(response % id)

def ort(request, id):
	response = "You're looking at the results of ort %s."
	return HttpResponse(response % id)

def strasse(request, id):
	response = "You're looking at the results of strasse %s."
	return HttpResponse(response % id)
