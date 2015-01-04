from django.conf.urls import patterns, url
from Fifa import views

urlpatterns = patterns('',
                       url(r'^league/new/', views.new_league, name='new_league'),
                       url(r'^player/new/(?P<league_id>\d+)/', views.new_player, name='new_player'),
                       url(r'^match/generate/(?P<league_id>\d+)/', views.generate_match, name='generate_match'),
                       url(r'^$', views.index, name='index'),
)
