"""
WSGI config for bloodsystem project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')

application = get_wsgi_application()
