from django.urls import path
from Klienten.views import FahrgastView, DienstleisterView, DSGVOView, DSGVOasPDFView, FahrgastAddView, FahrgastChangeView, FahrgastDeleteView
from Klienten.views import DienstleisterView, DienstleisterAddView, DienstleisterChangeView, DienstleisterDeleteView
from Klienten.views import OrtView, OrtAddView, OrtChangeView, OrtDeleteView
from Klienten.views import StrassenView, StrassenAddView, StrassenChangeView, StrassenDeleteView

app_name = 'Klienten'
urlpatterns = [
	path('fahrgaeste/', FahrgastView.as_view()),
	path('fahrgaeste/add/', FahrgastAddView.as_view()),
	path('fahrgaeste/<int:pk>/', FahrgastChangeView.as_view()),
	path('fahrgaeste/<int:pk>/delete/', FahrgastDeleteView.as_view()),
	path('dienstleister/', DienstleisterView.as_view()),
	path('dienstleister/add/', DienstleisterAddView.as_view()),
	path('dienstleister/<int:pk>/', DienstleisterChangeView.as_view()),
	path('dienstleister/<int:pk>/delete/', DienstleisterDeleteView.as_view()),
	path('fahrgaeste/<int:pk>/dsgvo/', DSGVOView.as_view()),
	path('fahrgaeste/<int:id>/dsgvoAsPDF/', DSGVOasPDFView.as_view()),
	path('orte/', OrtView.as_view()),
	path('orte/add/', OrtAddView.as_view()),
	path('orte/<int:pk>/', OrtChangeView.as_view()),
	path('orte/<int:pk>/delete/', OrtDeleteView.as_view()),
	path('strassen/', StrassenView.as_view()),
	path('strassen/add/', StrassenAddView.as_view()),
	path('strassen/<int:pk>/',  StrassenChangeView.as_view()),
	path('strassen/<int:pk>/delete/',  StrassenDeleteView.as_view()),	
]