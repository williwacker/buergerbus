from django.urls import path
from .views import TourenView, TourAddView, TourAddView2, TourChangeView, TourDeleteView
#from .forms import TourAddForm1, TourAddForm2

app_name = 'Tour'
urlpatterns = [
	path('touren/', TourenView.as_view()),
	path('tour/add/', TourAddView.as_view()),
	path('tour/add/<int:pk>/', TourAddView2.as_view()),
	path('touren/<int:pk>/', TourChangeView.as_view()),
	path('<int:pk>/delete/', TourDeleteView.as_view()),
]