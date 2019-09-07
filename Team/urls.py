from django.urls import path

from .views import FahrerView, FahrerAddView, FahrerChangeView, FahrerDeleteView
#from .views import BuerokraftView, BuerokraftAddView, BuerokraftChangeView, BuerokraftDeleteView

app_name = 'Team'
urlpatterns = [
    path('fahrer/', FahrerView.as_view()),
	path('fahrer/add/', FahrerAddView.as_view()),
	path('fahrer/<int:pk>/', FahrerChangeView.as_view()),
	path('fahrer/<int:pk>/delete/', FahrerDeleteView.as_view()),
#    path('buerokraft/', BuerokraftView.as_view()),
#	path('buerokraft/add/', BuerokraftAddView.as_view()),
#	path('buerokraft/<int:pk>/', BuerokraftChangeView.as_view()),
#	path('buerokraft/<int:pk>/delete/', BuerokraftDeleteView.as_view()),    
]