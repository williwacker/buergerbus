from django.urls import path
from Klienten.views import FahrgastView, DienstleisterView, DSGVOView, DSGVOasPDFView, FahrgastAddView, FahrgastChangeView, FahrgastDeleteView, DienstleisterAddView

app_name = 'Klienten'
urlpatterns = [
    path('fahrgaeste/', FahrgastView.as_view()),
    path('fahrgast/add/', FahrgastAddView.as_view()),
    path('<int:pk>/', FahrgastChangeView.as_view()),
    path('<int:pk>/delete/', FahrgastDeleteView.as_view()),
    path('dienstleister/', DienstleisterView.as_view()),
    path('dienstleister/add/', DienstleisterAddView.as_view()),
    path('<int:pk>/dsgvo/', DSGVOView.as_view()),
    path('<int:id>/dsgvoAsPDF/', DSGVOasPDFView.as_view()),
]