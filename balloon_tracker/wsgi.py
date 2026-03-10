"""
WSGI config for balloon_tracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.setrecursionlimit(2*10**9)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'balloon_tracker.settings')

application = get_wsgi_application()
