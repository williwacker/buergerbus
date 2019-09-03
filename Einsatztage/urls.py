from django.urls import path
from django.views.generic import TemplateView

from . import views
from Einsatztage.views import TourView, GeneratePDF, FahrtageListView, FahrtageChangeView, BuerotageListView, BuerotageChangeView

app_name = 'Einsatztage'
urlpatterns = [
    path('fahrer/', FahrtageListView.as_view()),
    path('fahrer/<int:pk>/', FahrtageChangeView.as_view()),
    path('fahrer/<int:id>/tour/', TourView.as_view()),
    path('fahrer/<int:id>/tourAsPDF/', GeneratePDF.as_view()),
    path('buero/', BuerotageListView.as_view()),
    path('buero/<int:pk>/', BuerotageChangeView.as_view()),    
]