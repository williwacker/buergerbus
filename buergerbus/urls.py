﻿"""buergerbus URL Configuration

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
#import debug_toolbar
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import PasswordChangeView
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from smart_selects import urls as smart_selects_urls

from Accounts.signals import *
from Accounts.views import MyPasswordChangeDoneView, MyPasswordChangeView
from Basis.views import BasisView

urlpatterns = [
    path('', BasisView.as_view(), name='home'),
    path('Accounts/', include('Accounts.urls')),
    path('Basis/', include('Basis.urls')),  
    path('accounts/password/change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', MyPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/logout_success/', TemplateView.as_view(template_name='registration/logout_success.html')),
    path('accounts/', include('django.contrib.auth.urls')),      
    path('Einsatzmittel/', include('Einsatzmittel.urls')),
    path('Tour/', include('Tour.urls')),
    path('Einsatztage/', include('Einsatztage.urls')),
    path('Klienten/', include('Klienten.urls')),
    path('Team/', include('Team.urls')),
    path('Faq/', include('Faq.urls')),
    path('admin/', admin.site.urls),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # ??Django JET dashboard URLS
    url(r'^logs/', include('logtailer.urls')),
    path('jsi18n', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

handler400 = 'Basis.views.my_custom_bad_request_view'
handler403 = 'Basis.views.my_custom_permission_denied_view'
handler404 = 'Basis.views.my_custom_page_not_found_view'
handler500 = 'Basis.views.my_custom_error_view'

admin.site.site_header = "Bürgerbus Admin"
admin.site.site_title = "Alzey-Land Bürgerbus Portal"
admin.site.index_title = "Willkommen zum Bürgerbus Portal der VG Alzey-Land"
