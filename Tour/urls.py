from django.urls import path

from .views import (TourAddView, TourAddView2, TourChangeView, TourCopyView, TourDeleteView,
                    TourView)

#from .forms import TourAddForm1, TourAddForm2

app_name = 'Tour'
urlpatterns = [
	path('tour/', TourView.as_view()),
	path('tour/add/', TourAddView.as_view()),
	path('tour/add/<int:pk>/', TourAddView2.as_view()),
	path('tour/<int:pk>/', TourChangeView.as_view()),
	path('tour/<int:pk>/copy/', TourCopyView.as_view()),
	path('tour/<int:pk>/delete/', TourDeleteView.as_view()),
]
