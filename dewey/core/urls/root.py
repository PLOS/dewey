from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings

from dewey.core.urls import api_v1
from dewey.core.forms import CrispyAuthenticationForm
from dewey.environments import urls as enviro_urls, views as enviro_frontend
from dewey.environments.api import views as enviro_views

from dewey.networks import urls as networks_urls
from dewey.salt import urls as salt_urls



urlpatterns = [
    url(r'^$', enviro_frontend.hosts_list, name='index'),
    url(r'^accounts/login/$', auth_views.login, {
            'template_name': 'dewey/login.html',
            'authentication_form': CrispyAuthenticationForm
        }, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'template_name': 'dewey/logout.html'}, name='logout'),
    url(r'^accounts/password/reset/request/$', RedirectView.as_view(url=settings.PASSWORD_RESET_URL, permanent=False), name='password_reset'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api_v1, namespace='api_v1')),
    url(r'^hosts/', include(enviro_urls)),
    url(r'^environments/', include(enviro_urls)),
    url(r'^export/secrets', enviro_views.export_secrets, name='export-secrets'),
    url(r'^networks/', include(networks_urls)),
    url(r'^salt/', include(salt_urls, namespace='salt')),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass
    if settings.FRONTEND == 'gunicorn':
        from django.conf.urls.static import static
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

