from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.views.generic import TemplateView

from Basis.models import Document
from Basis.views import (
    DocumentAddView, DocumentChangeView, DocumentDeleteView, DocumentListView,
    DocumentPDFView, FeedbackView, GroupAddView, GroupChangeView,
    GroupDeleteView, GroupView, UserAddView, UserChangeView, UserDeleteView,
    UserView, RestartApache)

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
    path('restart_apache/', RestartApache.as_view(), name='restart_apache'),
    path('feedback/', FeedbackView.as_view()),
    path('documents/', DocumentListView.as_view()),
    path('documents/add/', DocumentAddView.as_view()),
    path('documents/<int:pk>/', DocumentChangeView.as_view()),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view()),
    path('documents/<int:pk>/view/<str:str>.pdf', DocumentPDFView.as_view()),
] 
