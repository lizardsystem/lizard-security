# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
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
    # url(r'^something/',
    #     direct.import.views.some_method,
    #     name="name_it"),
    )
urlpatterns += debugmode_urlpatterns()
