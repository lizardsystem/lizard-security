# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls import include
from django.conf.urls import patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    )
