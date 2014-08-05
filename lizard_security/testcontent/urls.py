# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin

import lizard_security.urls
import lizard_security.testcontent.views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        lizard_security.testcontent.views.overview,
        name="overview"),
    (r'^admin/', include(admin.site.urls)),
    (r'^security/', include(lizard_security.urls)),
    )
