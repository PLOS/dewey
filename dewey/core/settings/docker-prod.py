from .common import *
import os

DEBUG = False

HOME = os.environ.get('HOME')

STATIC_ROOT = os.path.join(HOME, 'static')

SITE_PROTOCOL = 'https'
SITE_DOMAIN = 'dewey.soma.plos.org'

LOGGING['loggers']['django']['handlers'] = ['gunicorn']
LOGGING['loggers']['dewey']['handlers'] = ['gunicorn']
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['dewey']['level'] = 'INFO'
