from django.conf.urls import include, url
from rest_framework import routers

from dewey.networks.api import views as api

router = routers.SimpleRouter()
router.register(r'networks/networks', api.NetworkViewSet, base_name='networks-networks'),
router.register(r'networks/assignments', api.AddressAssignmentViewSet, base_name='networks-assignments')

urlpatterns = [
    url(r'^networks/$', api.api_root, name='networks-api-root'),
    url(r'', include((router.urls, 'networks'))),
    url(r'^networks/networks/(?P<slug>[\w\d-]+)/unused/$', api.get_unused_address, name='networks-unused')
]