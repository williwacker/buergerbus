from django.urls import path
from django.views.generic import TemplateView

from Einsatztage.views import (BuerotageBookView, BuerotageCancelView,
                               BuerotageChangeView, BuerotageListView,
                               FahrplanAsCSV, FahrplanAsPDF,
                               FahrplanBackupView, FahrplanEmailView,
                               FahrplanView, FahrtageAddView,
                               FahrtageBooknView, FahrtageBookvView,
                               FahrtageCancelnView, FahrtageCancelvView,
                               FahrtageChangeView, FahrtageDeleteView,
                               FahrtageListView)

from . import views

app_name = 'Einsatztage'
urlpatterns = [
    path('fahrer/', FahrtageListView.as_view()),
    path('fahrer/add/', FahrtageAddView.as_view()),
    path('fahrer/fahrplanBackup/', FahrplanBackupView.as_view()),
    path('fahrer/<int:pk>/', FahrtageChangeView.as_view()),
    path('fahrer/<int:pk>/bookv/', FahrtageBookvView.as_view()),
    path('fahrer/<int:pk>/bookn/', FahrtageBooknView.as_view()),
    path('fahrer/<int:pk>/cancelv/', FahrtageCancelvView.as_view()),
    path('fahrer/<int:pk>/canceln/', FahrtageCancelnView.as_view()),
    path('fahrer/<int:pk>/delete/', FahrtageDeleteView.as_view()),
    path('fahrer/<int:id>/fahrplan/', FahrplanView.as_view()),
    path('fahrer/<int:id>/fahrplanAsPDF/', FahrplanAsPDF.as_view()),
    path('fahrer/<int:id>/fahrplanAsEmail/', FahrplanEmailView.as_view()),
    path('fahrer/<int:id>/fahrplanAsCSV/', FahrplanAsCSV.as_view()),
    path('buero/', BuerotageListView.as_view()),
    path('buero/<int:pk>/', BuerotageChangeView.as_view()),
    path('buero/<int:pk>/book/', BuerotageBookView.as_view()),
    path('buero/<int:pk>/cancel/', BuerotageCancelView.as_view()),
]
