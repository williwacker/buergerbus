from django.urls import path
from django.views.generic import TemplateView

from . import views
from Einsatztage.views import FahrtageView, TourView, GeneratePDF, FahrtageDetailView, BueroView, BueroDetailView

app_name = 'Einsatztage'
urlpatterns = [
    path('fahrer/', FahrtageView.as_view()),
    path('fahrer/<int:pk>/', FahrtageDetailView.as_view()),
    path('fahrer/<int:id>/tour/', TourView.as_view()),
    path('fahrer/<int:id>/tourAsPDF/', GeneratePDF.as_view()),
    path('buero/', BueroView.as_view()),
    path('buero/<int:pk>/', BueroDetailView.as_view()),    
]