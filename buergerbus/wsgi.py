"""
WSGI config for buergerbus project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

for f in sys.path:
    print(f)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buergerbus.settings')

application = get_wsgi_application()
