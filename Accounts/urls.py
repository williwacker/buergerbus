from django.conf import settings
from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from .views import (GroupAddView, GroupChangeView, GroupDeleteView,
                         GroupView, ProfileChangeView, ProfileView,
                         UserAddView, UserChangeView, UserDeleteView, UserView)

app_name = 'Accounts'
urlpatterns = [
    path('benutzer/', UserView.as_view(), name='userview'),
    path('benutzer/add/', UserAddView.as_view(), name='userview_add'),
    path('benutzer/<int:pk>/', UserChangeView.as_view(), name='userview_chg'),
    path('benutzer/<int:pk>/delete/', UserDeleteView.as_view(), name='userview_delete'),
    path('gruppen/', GroupView.as_view(), name='groupview'),
    path('gruppen/add/', GroupAddView.as_view(), name='groupview_add'),
    path('gruppen/<int:pk>/', GroupChangeView.as_view(), name='groupview_chg'),
    path('gruppen/<int:pk>/delete/', GroupDeleteView.as_view(), name='groupview_delete'),
    path('logout_success/', TemplateView.as_view(template_name='Basis/logout_success.html'), name='logout_success'),
    path('profile/', ProfileView.as_view(), name='profileview'),
    path('profile/<int:pk>/', ProfileChangeView.as_view(), name='profileview_chg'),  
]
