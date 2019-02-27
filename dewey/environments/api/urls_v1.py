from django.conf.urls import url, include
from rest_framework_nested import routers

from dewey.environments.api import views as rest_views

router = routers.SimpleRouter()
router.register(r'environments/clusters', rest_views.ClusterViewSet, base_name='environments-clusters')
router.register(r'environments/environments', rest_views.EnvironmentViewSet, base_name='environments-environments')
router.register(r'environments/hosts', rest_views.HostViewSet, base_name='environments-hosts')
router.register(r'environments/roles', rest_views.RoleViewSet, base_name='environments-roles')

hosts_router = routers.NestedSimpleRouter(router, 'environments/hosts', lookup='host')
hosts_router.register(r'secrets', rest_views.SaltHostSecretsViewSet, base_name='host-secrets')

urlpatterns = [
    url(r'^environments/$', rest_views.api_root, name='environments-api-root'),
    url(r'', include((router.urls, 'environments'))),
    url(r'', include((hosts_router.urls, 'environments')))
]