from django.urls import path

from .views import (TourAcceptView, TourAddView, TourAddView2, TourChangeView,
                    TourCopyView, TourDeleteView, TourView)

app_name = 'Tour'
urlpatterns = [
	path('tour/', TourView.as_view()),
	path('tour/add/', TourAddView.as_view()),
	path('tour/add/<int:pk>/', TourAddView2.as_view()),
	path('tour/<int:pk>/', TourChangeView.as_view()),
	path('tour/<int:pk>/copy/', TourCopyView.as_view()),
	path('tour/<int:pk>/accept/', TourAcceptView.as_view()),
	path('tour/<int:pk>/delete/', TourDeleteView.as_view()),
]
