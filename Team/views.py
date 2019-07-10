from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Fahrer

def index(request):
	fahrer_liste = Fahrer.objects.order_by('name')
	context = {'fahrer_liste':fahrer_liste}
	return render(request, 'Team/index.html', context)

def detail(request, id):
    details = get_object_or_404(Fahrer, pk=id)
    context = {'details':details}
    print(details)
    return render(request, 'Team/detail.html', context)

def results(request, id):
	response = "You're looking at the results of Team %s."
	return HttpResponse(response % name_id)
