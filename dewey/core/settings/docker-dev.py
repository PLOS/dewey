from .common import *

HOME = os.environ.get('HOME')

STATIC_ROOT = os.path.join(HOME, 'static')

DEBUG = True

SITE_PROTOCOL = 'http'
SITE_DOMAIN = 'localhost:8080'
ALLOWED_HOSTS.append('localhost')

TASKS_ENABLED = False
