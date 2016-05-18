from django.conf.urls import include, url, patterns
from rest_framework.routers import SimpleRouter

from views import LeagueViewSet


router = SimpleRouter()
router.register(r'leagues', LeagueViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)))