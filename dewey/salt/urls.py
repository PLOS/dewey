from django.conf.urls import url

from dewey.salt import views


urlpatterns = [
    url(r'^$', views.highstates_list, name='highstates_index'),
    url(r'^highstate/(?P<id>\d+)/$', views.highstate_detail, name='highstate_detail'),
    url(r'^highstates/$', views.highstates_list, name='highstates_list'),
    url(r'^highstates/changes/$', views.statechanges_list, name='statechanges_list'),
    url(r'^change/(?P<id>\d+)/$', views.change_detail, name='change_detail'),
    url(r'^change/(?P<id>\d+)/diff/$', views.diff_enlarge, name='diff_enlarge'),
    url(r'^change/(?P<id>\d+)/diff/txt/$', views.diff_txt, name='diff_txt'),
    url(r'^highstates/errors/$', views.stateerrors_list, name='stateerrors_list'),
]