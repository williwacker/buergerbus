from django.urls import path

from . import views

app_name = 'Klienten'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:name_id>/', views.detail, name='detail'),
    path('<int:name_id>/results/', views.results, name='results'),
    path('<int:name_id>/ort/', views.ort, name='ort'),
    path('<int:name_id>/strasse/', views.strasse, name='strasse'),
]