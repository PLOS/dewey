"""dewey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from hardware import views as hardware_views
from hosts import rest_urls as hosts_rest_urls
from hosts import views as hosts_views
from hosts import urls as hosts_urls


router = DefaultRouter()
router.register(r'hosts', hosts_views.HostViewSet)
router.register(r'host-roles', hosts_views.HostRoleViewSet)
router.register(r'clusters', hosts_views.ClusterViewSet)
router.register(r'servers', hardware_views.ServerViewSet)
router.register(r'pdus', hardware_views.PowerDistributionUnitViewSet)
router.register(r'network-devices', hardware_views.NetworkDeviceViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^hosts/', include(hosts_urls)),
    #url(r'^api/hosts/', include(hosts_rest_urls))
]
