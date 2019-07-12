"""buergerbus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf.urls import url
from smart_selects import urls as smart_selects_urls


urlpatterns = [
    path('Einsatzmittel/', include('Einsatzmittel.urls')),
    path('Team/', include('Team.urls')),
    path('Einsatztage/', include('Einsatztage.urls')),
    path('Klienten/', include('Klienten.urls')),
    path('', admin.site.urls),
    path('admin/', admin.site.urls),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')), #˓→Django JET dashboard URLS
#    url(r'^admin/', include('admin.site.urls')),
]

admin.site.site_header = "Bürgerbus Admin"
admin.site.site_title = "Alzey-Land Bürgerbus Portal"
admin.site.index_title = "Willkommen zum Bürgerbus Portal der VG Alzey-Land"

