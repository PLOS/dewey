from .common import *

HOME = os.environ.get('HOME')

STATIC_ROOT = os.path.join(HOME, 'static')

DEBUG = True

SITE_PROTOCOL = 'http'
SITE_DOMAIN = 'localhost:8080'
ALLOWED_HOSTS.append('localhost')

TASKS_ENABLED = False

CELERY_BROKER_URL = os.getenv('DEWEY_CELERY_BROKER_URL', 'redis://localhost:6379/0')

# Setup logging to gunicorn
LOGGING['handlers']['gunicorn'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}

# Tell django and dewey to log to gunicorn
LOGGING['loggers'] = {
    'django': {
        'handlers': ['gunicorn'],
        'propagate': True,
        'level': 'DEBUG',
    },
    'dewey': {
        'handlers': ['gunicorn'],
        'level': 'DEBUG',
        'propagate': True,
    },
}