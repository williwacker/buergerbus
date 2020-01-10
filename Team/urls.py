from django.urls import path

from .views import (FahrerAddView, FahrerChangeView, FahrerCopyView, FahrerDeleteView,
                    FahrerView, KoordinatorAddView, KoordinatorChangeView,
                    KoordinatorDeleteView, KoordinatorView)

app_name = 'Team'
urlpatterns = [
    path('fahrer/', FahrerView.as_view()),
	path('fahrer/add/', FahrerAddView.as_view()),
	path('fahrer/<int:pk>/', FahrerChangeView.as_view()),
	path('fahrer/<int:pk>/copy/', FahrerCopyView.as_view()),
	path('fahrer/<int:pk>/delete/', FahrerDeleteView.as_view()),
    path('koordinator/', KoordinatorView.as_view()),
	path('koordinator/add/', KoordinatorAddView.as_view()),
	path('koordinator/<int:pk>/', KoordinatorChangeView.as_view()),
	path('koordinator/<int:pk>/delete/', KoordinatorDeleteView.as_view()),    
]
