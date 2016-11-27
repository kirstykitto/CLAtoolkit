"""
WSGI config for clatoolkit_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import dotenv

from django.core.wsgi import get_wsgi_application
# .env file has to be loaded in settings.py so that the toolkit will run properly on Nector server.
# (manage.py won't be executed in environment where .wsgi file is used.)
#dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clatoolkit_project.settings")

application = get_wsgi_application()
