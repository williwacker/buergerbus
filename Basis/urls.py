from django.urls import path
from django.views.generic import TemplateView

#from . import views
from .views_auth import UserView, UserAddView, UserChangeView, UserDeleteView
from .views_auth import GroupView, GroupAddView, GroupChangeView, GroupDeleteView

app_name = 'Basis'
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
]