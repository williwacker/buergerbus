from django.urls import path

from . import views

app_name = 'Tour'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.detail, name='detail'),
    path('<int:id>/results/', views.results, name='results'),
]