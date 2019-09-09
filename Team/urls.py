from django.urls import path

from .views import FahrerView, FahrerAddView, FahrerChangeView, FahrerDeleteView
from .views import KoordinatorView, KoordinatorAddView, KoordinatorChangeView, KoordinatorDeleteView

app_name = 'Team'
urlpatterns = [
    path('fahrer/', FahrerView.as_view()),
	path('fahrer/add/', FahrerAddView.as_view()),
	path('fahrer/<int:pk>/', FahrerChangeView.as_view()),
	path('fahrer/<int:pk>/delete/', FahrerDeleteView.as_view()),
    path('koordinator/', KoordinatorView.as_view()),
	path('koordinator/add/', KoordinatorAddView.as_view()),
	path('koordinator/<int:pk>/', KoordinatorChangeView.as_view()),
	path('koordinator/<int:pk>/delete/', KoordinatorDeleteView.as_view()),    
]