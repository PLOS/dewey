from .common import *
import os

HOME = os.environ.get('HOME')

STATIC_ROOT = os.path.join(HOME, 'static')

DEBUG = True

SITE_PROTOCOL = 'http'
SITE_DOMAIN = 'dewey.sfo.plos.org'
ALLOWED_HOSTS.append('localhost')

TASKS_ENABLED = False
