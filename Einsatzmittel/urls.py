from django.urls import path

from . import views

app_name = 'Bus'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:bus_id>/', views.detail, name='detail'),
    path('<int:bus_id>/results/', views.results, name='results'),
]