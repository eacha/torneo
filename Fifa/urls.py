from django.conf.urls import patterns, url
from Fifa import views

urlpatterns = patterns('',
                       url(r'^login/', views.login_view, name='login'),
                       url(r'^logout/', views.logout_view, name='logout'),
                       url(r'^register/', views.register, name='register'),
                       url(r'^leagues/', views.league_list, name='leagues'),
                       url(r'^league/details/(?P<league_id>\d+)/', views.league_details, name='league_details'),

                       url(r'^league/registration/(?P<league_id>\d+)/', views.finish_registration, name='end_league_registration'),
                       # url(r'^player/new/(?P<league_id>\d+)/', views.new_player, name='new_player'),
                       url(r'^match/generate/(?P<league_id>\d+)/', views.generate_match, name='generate_match'),
                       url(r'^match/result/(?P<match_id>\d+)/', views.set_result, name='set_match_result'),

                       url(r'^cover/', views.cover, name='cover'),
                       url(r'^inicio/', views.inicio, name='inicio'),
                       url(r'^administration/leagues/end/(?P<league_id>\d+)/', views.end_league, name='end_league'),
                       url(r'^administration/leagues/edit/(?P<league_id>\d+)/', views.edit_league, name='edit_league'),
                       url(r'^administration/leagues/new/', views.new_league, name='new_league'),
                       url(r'^administration/leagues/', views.admin_leagues, name='admin_leagues'),
                       url(r'^administration/', views.administration, name='administration'),




                       url(r'^$', views.index, name='index'),
)
