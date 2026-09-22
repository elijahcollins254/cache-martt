"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``app``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import logging
from pathlib import Path

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

if os.getenv('VERCEL') == '1' or os.getenv('RUN_DJANGO_MIGRATIONS') == '1':
	logging.basicConfig(level=logging.INFO)
	logging.getLogger(__name__).info('Applying Django migrations before starting the Vercel app')
	call_command('migrate', interactive=False, verbosity=1)

app = get_wsgi_application()

# Serve static files with WhiteNoise
BASE_DIR = Path(__file__).resolve().parent.parent
STATICFILES_ROOT = os.path.join(str(BASE_DIR), 'staticfiles')

# WhiteNoise will serve files from staticfiles directory
app = WhiteNoise(app, root=STATICFILES_ROOT, max_age=31536000)
