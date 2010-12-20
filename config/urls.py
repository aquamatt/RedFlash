# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details

from django.conf.urls.defaults import *
from squawk.views import contact_request
from squawk.views import group_request
from squawk.views import event_request

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^t/', include('t.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # API urls
    (r'contact/(?P<slug>[a-zA-Z0-9_\-]*)/$', contact_request),
    (r'group/(?P<slug>[a-zA-Z0-9_\-]*)/$', group_request),
    (r'event/(?P<slug>[a-zA-Z0-9_\-]*)/$', event_request),
)
