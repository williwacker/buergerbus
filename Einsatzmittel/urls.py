from django.urls import path

from . import views
from .views import (BueroAddView, BueroChangeView, BueroDeleteView, BueroView,
                    BusAddView, BusChangeView, BusDeleteView, BusView)

app_name = 'Einsatzmittel'
urlpatterns = [
    path('busse/', BusView.as_view()),
    path('busse/add/', BusAddView.as_view()),
    path('busse/<int:pk>/', BusChangeView.as_view()),
    path('busse/<int:pk>/delete/', BusDeleteView.as_view()),
    path('bueros/', BueroView.as_view()),
    path('bueros/add/', BueroAddView.as_view()),
    path('bueros/<int:pk>/', BueroChangeView.as_view()),
    path('bueros/<int:pk>/delete/', BueroDeleteView.as_view()),
]
