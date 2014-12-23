from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from Fifa.forms import LeagueForm


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
    return HttpResponse("New Player")


def generate_match(request, league_id):
    return HttpResponse("Generate Match")