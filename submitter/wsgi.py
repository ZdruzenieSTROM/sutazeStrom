import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'submitter.settings.test_settings')

application = get_wsgi_application()
