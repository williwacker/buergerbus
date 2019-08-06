from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.generic import View
from datetime import datetime

from .models import Tour

def index(request):
    tour_liste = Tour.objects.order_by('id')
    print(tour_liste)
    context = {'tour_liste':tour_liste}
    return render(request, 'Tour/index.html', context)

def detail(request, id):
    details = get_object_or_404(Tour, pk=id)
    context = {'details':details}
    print(details)
    return render(request, 'Tour/detail.html', context)

def results(request, id):
	response = "You're looking at the results of Tour %s."
	return HttpResponse(response % id)
