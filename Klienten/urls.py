from django.urls import path
from Klienten.views import FahrgastView, DienstleisterView, DSGVOView, DSGVOasPDFView, FahrgastAddView, FahrgastChangeView, FahrgastDeleteView
from Klienten.views import DienstleisterView, DienstleisterAddView, DienstleisterChangeView, DienstleisterDeleteView
from Klienten.views import OrtView, OrtAddView, OrtChangeView, OrtDeleteView

app_name = 'Klienten'
urlpatterns = [
	path('fahrgaeste/', FahrgastView.as_view()),
	path('fahrgast/add/', FahrgastAddView.as_view()),
	path('fahrgast/<int:pk>/', FahrgastChangeView.as_view()),
	path('fahrgast/<int:pk>/delete/', FahrgastDeleteView.as_view()),
	path('dienstleister/', DienstleisterView.as_view()),
	path('dienstleister/add/', DienstleisterAddView.as_view()),
	path('dienstleister/<int:pk>/', DienstleisterChangeView.as_view()),
	path('dienstleister/<int:pk>/delete/', DienstleisterDeleteView.as_view()),
	path('fahrgast/<int:pk>/dsgvo/', DSGVOView.as_view()),
	path('fahrgast/<int:id>/dsgvoAsPDF/', DSGVOasPDFView.as_view()),
	path('orte/', OrtView.as_view()),
	path('ort/add/', OrtAddView.as_view()),
	path('ort/<int:pk>/', OrtChangeView.as_view()),
	path('ort/<int:pk>/delete/', OrtDeleteView.as_view()),
]