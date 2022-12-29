"""
WSGI config for innotter project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

print(f"WSGI.PY --- {os.environ.get('DJANGO_SETTINGS_MODULE')}")
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'innotter.wsgi.app')

app = get_wsgi_application()
