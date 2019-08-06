from django.urls import path
from django.views.generic import TemplateView

from . import views
from Einsatztage.views import FahrtageView, TourView, GeneratePDF, FahrtageDetailView

app_name = 'Einsatztage'
urlpatterns = [
    path('', FahrtageView.as_view()),
    path('<int:pk>/', FahrtageDetailView.as_view()),
    path('<int:id>/tour/', TourView.as_view()),
    path('<int:id>/tourAsPDF/', GeneratePDF.as_view()),
]