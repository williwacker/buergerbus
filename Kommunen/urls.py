from django.urls import path, re_path
from Kommunen.views import KommunenView, KommuneAddView, KommuneChangeView, KommuneDeleteView

app_name = 'Kommunen'
urlpatterns = [
	path('kommunen/', KommunenView.as_view()),
	path('kommunen/add/', KommuneAddView.as_view()),
	path('kommunen/<int:pk>/', KommuneChangeView.as_view()),
	path('kommunen/<int:pk>/delete/', KommuneDeleteView.as_view()),
]