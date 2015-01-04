from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Torneo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'Fifa.views.index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^fifa/', include('Fifa.urls')),
)
