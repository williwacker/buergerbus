from django.urls import path

from . import views
from Basis.views import BasisView

app_name = 'Basis'
urlpatterns = [
    path('', BasisView.as_view()),

]