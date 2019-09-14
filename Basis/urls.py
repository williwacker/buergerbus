from django.urls import path
from django.views.generic import TemplateView

#from . import views
from .views_auth import UserView, UserAddView, UserChangeView, UserDeleteView
from .views_auth import GroupView, GroupAddView, GroupChangeView, GroupDeleteView

app_name = 'Basis'
urlpatterns = [
    path('benutzer/', UserView.as_view()),
    path('benutzer/add/', UserAddView.as_view()),
    path('benutzer/<int:pk>/', UserChangeView.as_view()),
    path('benutzer/<int:pk>/delete/', UserDeleteView.as_view()),
    path('gruppen/', GroupView.as_view()),
    path('gruppen/add/', GroupAddView.as_view()),
    path('gruppen/<int:pk>/', GroupChangeView.as_view()),
    path('gruppen/<int:pk>/delete/', GroupDeleteView.as_view()),
    path('logout_success/', TemplateView.as_view(template_name='Basis/logout_success.html')),
]