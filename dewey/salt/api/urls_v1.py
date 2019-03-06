from django.conf.urls import include, url
from rest_framework_nested import routers

from dewey.salt.api import views as api
from dewey.environments.api import views as env_api

router = routers.SimpleRouter()
router.register(r'salt/changes', api.ChangeViewSet, base_name='salt-changes')
router.register(r'salt/highstates', api.HighstateViewSet, base_name='salt-highstates')
router.register(r'salt/hosts', env_api.SaltHostViewSet, base_name='salt-hosts')

events_router = routers.NestedSimpleRouter(router, 'salt/highstates', lookup='highstate')
events_router.register(r'changes', api.StateChangeViewSet, base_name='highstate-changes')
events_router.register(r'errors', api.StateErrorViewSet, base_name='highststate-errors')

hosts_router = routers.NestedSimpleRouter(router, 'salt/hosts', lookup='host')
hosts_router.register(r'secrets', env_api.SaltHostSecretsViewSet, base_name='host-secrets')

urlpatterns = [
    url(r'', include((router.urls, 'salt'))),
    url(r'', include((events_router.urls, 'salt'))),
    url(r'', include((hosts_router.urls, 'salt'))),
    url(r'^salt/discovery/(?P<environment>\w+)/$', env_api.salt_discovery_view, name='salt-discovery'),
    url(r'^salt/secrets/(?P<environment>[\w]+)/(?P<role>[\w.-]+)/$', env_api.role_secrets,
        name='role-secrets'),
    url(r'^salt/$', api.api_root, name='salt-api-root'),
]
