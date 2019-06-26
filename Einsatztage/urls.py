from django.urls import path

from . import views

app_name = 'Einsatztage'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:einsatztag_id>/', views.detail, name='detail'),
    path('<int:einsatztag_id>/results/', views.results, name='results'),
]