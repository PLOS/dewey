from rest_framework_swagger.views import get_swagger_view
from django.conf.urls import include, url

from dewey.environments.api import urls_v1 as environments_api
from dewey.networks.api import urls_v1 as networks_api
from dewey.salt.api import urls_v1 as salt_api

app_name = 'api_v1'
schema_view = get_swagger_view(title='Dewey API')

urlpatterns = [
    url(r'', include(environments_api)),
    url(r'', include(networks_api)),
    url(r'', include(salt_api)),
    url(r'^$', schema_view, name='doc'),
]