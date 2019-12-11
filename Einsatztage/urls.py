from django.urls import path
from django.views.generic import TemplateView

from . import views
from Einsatztage.views import FahrplanView, FahrplanAsPDF, FahrplanEmailView, FahrplanAsCSV, FahrplanBackupView 
from Einsatztage.views import FahrtageListView, FahrtageChangeView
from Einsatztage.views import BuerotageListView, BuerotageChangeView

app_name = 'Einsatztage'
urlpatterns = [
    path('fahrer/', FahrtageListView.as_view()),
    path('fahrer/fahrplanBackup/', FahrplanBackupView.as_view()),
    path('fahrer/<int:pk>/', FahrtageChangeView.as_view()),
    path('fahrer/<int:id>/fahrplan/', FahrplanView.as_view()),
    path('fahrer/<int:id>/fahrplanAsPDF/', FahrplanAsPDF.as_view()),
    path('fahrer/<int:id>/fahrplanAsEmail/', FahrplanEmailView.as_view()),
    path('fahrer/<int:id>/fahrplanAsCSV/', FahrplanAsCSV.as_view()),
    path('buero/', BuerotageListView.as_view()),
    path('buero/<int:pk>/', BuerotageChangeView.as_view()),
]