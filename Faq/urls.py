from django.urls import path

from Faq.views import (QuestionAddView, QuestionAdminChangeView,
                       QuestionAdminDeleteView, QuestionAdminListView,
                       QuestionListView, QuestionTopicView, TopicAddView,
                       TopicChangeView, TopicDeleteView, TopicView)

from . import views

app_name = 'Faq'
urlpatterns = [
    path('topics/admin/', TopicView.as_view()),
    path('topics/admin/add/', TopicAddView.as_view()),
    path('topics/admin/<int:pk>/', TopicChangeView.as_view()),
    path('topics/admin/<int:pk>/delete/', TopicDeleteView.as_view()),

    path('questions/admin/', QuestionAdminListView.as_view()),
    path('questions/admin/add/', QuestionAddView.as_view()),
    path('questions/admin/<int:pk>/', QuestionAdminChangeView.as_view()),
    path('questions/admin/<int:pk>/delete/', QuestionAdminDeleteView.as_view()),

    path('questions/', QuestionTopicView.as_view()),
    path('questions/list/', QuestionListView.as_view()),
    path('questions/list/add/', QuestionAddView.as_view()),

]
