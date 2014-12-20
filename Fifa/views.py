from django.http.response import HttpResponse
from django.shortcuts import render


def new_league(request):
    return HttpResponse("New League")


def new_player(request, league_id):
    return HttpResponse("New Player")


def generate_match(request, league_id):
    return HttpResponse("Generate Match")