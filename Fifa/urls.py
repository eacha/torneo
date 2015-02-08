from django.conf.urls import patterns, url
from django.contrib.auth.views import password_reset
from Fifa import views
from Fifa.forms import ResetPasswordForm

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
                       url(r'^administration/players/edit/(?P<player_id>\d+)/', views.edit_player, name='edit_player'),
                       url(r'^administration/weeks/', views.admin_weeks, name='admin_weeks'),
                       url(r'^administration/players/', views.admin_players, name='admin_players'),
                       url(r'^administration/', views.administration, name='administration'),

                       url(r'^user/password/reset/$',
                           'django.contrib.auth.views.password_reset',
                           {'post_reset_redirect': '/fifa/user/password/reset/done/',
                            'template_name': 'Fifa/password_reset_form.html',
                            'email_template_name': 'Fifa/password_reset_email.html'},
                           name="password_reset"),

                       url(r'^user/password/reset/done/$',
                           'django.contrib.auth.views.password_reset_done',
                           {'template_name': 'Fifa/password_reset_done.html'}),

                       url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'django.contrib.auth.views.password_reset_confirm',
                           {'post_reset_redirect': '/fifa/user/password/done/',
                            'template_name': 'Fifa/password_reset_confirm.html',
                            'set_password_form': ResetPasswordForm},
                           name='password_reset_confirm'),

                       url(r'^user/password/done/$',
                           'django.contrib.auth.views.password_reset_complete',
                           {'template_name': 'Fifa/password_reset_complete.html'}),




                       url(r'^$', views.inicio, name='index'),
                       )
