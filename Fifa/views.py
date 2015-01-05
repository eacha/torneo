from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from Fifa.forms import LeagueForm, PlayerForm
from Fifa.models import League, Player


def new_league(request):
    if request.POST:
        form = LeagueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = LeagueForm()
    return render(request, 'fifa/league_form.html', {'form': form})


def new_player(request, league_id):
    league = get_object_or_404(League, id=league_id)
    if request.POST:
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.league = league
            player.save()

            return HttpResponseRedirect('/')
    else:
        form = PlayerForm()
    return render(request, 'fifa/player_form.html', {'form': form, 'league': league})

def generate_match(request, league_id):
    return HttpResponse("Generate Match")


def index(request):
    leagues = League.objects.all()
    return render(request, 'fifa/index.html', {'leagues': leagues})

def admin_league(request, league_id):
    league = get_object_or_404(League, id=league_id)
    players = Player.objects.filter(league=league)
    return render(request,'fifa/league_admin.html', {'league': league, 'players': players})