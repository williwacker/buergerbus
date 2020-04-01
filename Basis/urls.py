from django.conf import settings
from django.conf.urls import url
from django.urls import path

from Basis.models import Document
from Basis.views import (
    CoffeeView, DocumentAddView, DocumentChangeView, DocumentDeleteView,
    DocumentListView, DocumentPDFView, FeedbackView, RestartApache,
    StatisticView)

app_name = 'Basis'
urlpatterns = [
    path('restart_apache/', RestartApache.as_view(), name='restart_apache'),
    path('feedback/', FeedbackView.as_view()),
    path('documents/', DocumentListView.as_view()),
    path('documents/add/', DocumentAddView.as_view()),
    path('documents/<int:pk>/', DocumentChangeView.as_view()),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view()),
    path('documents/<int:pk>/view/<str:str>.pdf', DocumentPDFView.as_view()),
    path('coffee/', CoffeeView.as_view()),
    path('statistics/', StatisticView.as_view()),
]
