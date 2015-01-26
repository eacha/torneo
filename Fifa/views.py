from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from Fifa.forms import LeagueForm, PlayerForm, RegistrationForm, LoginForm
from Fifa.models import League, Player, Match, PositionTable
from Fix.Fixture import Fixture


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
    league = get_object_or_404(League, id=league_id)
    if not league.start:
        players = Player.objects.filter(league=league)
        # Created Position Table
        for player in players:
            position = PositionTable(league=league,
                                     player=player)
            position.save()
        # Created Matchs
        fix = Fixture(list(players))
        fixture = fix.generate()
        counter = 1

        for round in fixture:
            for match in round:
                element = Match(league=league,
                                local=match[0],
                                visit=match[1],
                                week=counter,
                                local_score=-1,
                                visit_score=-1)
                element.save()
            counter += 1

        # set league properties
        matches = Match.objects.filter(league=league).count()
        league.registration = False
        league.start = True
        league.total_matches = matches
        league.save()
    return HttpResponseRedirect(reverse('league_details', args=(league.id,)))


def index(request):
    leagues = League.objects.filter(start=True)
    if leagues is not None:
        tables = []
        matches = []
        for league in leagues:
            table = PositionTable.objects.filter(league=league)
            tables.append(table)
        return render(request, 'fifa/index.html', {'leagues': leagues, 'tables': tables})
    return render(request, 'fifa/index.html')


def league_details(request, league_id):
    league = get_object_or_404(League, id=league_id)
    players = Player.objects.filter(league=league)
    if league.start:
        matches = Match.objects.filter(league=league).order_by('week')
        return render(request, 'fifa/league_details.html', {'league': league, 'players': players, 'matches': matches})
    return render(request, 'fifa/league_details.html', {'league': league, 'players': players})


def finish_registration(request, league_id):
    league = get_object_or_404(League, id=league_id)
    league.registration = False
    league.save()
    return HttpResponseRedirect(reverse('league_details', args=(league.id,)))


def set_result(request, match_id):
    if request.POST:

        # Setting the match result
        match = get_object_or_404(Match, id=match_id)
        local = int(request.POST.get("local", ""))
        visit = int(request.POST.get("visit", ""))
        match.local_score = local
        match.visit_score = visit
        match.save()

        # Upload the position table
        player1 = PositionTable.objects.get(player=match.local)
        player2 = PositionTable.objects.get(player=match.visit)
        # Wins, Losses, Draws and Points
        print local
        print visit
        if local > visit:
            player1.wins += 1
            player2.losses += 1
            player1.points += 3
        elif local < visit:
            player1.losses += 1
            player2.wins += 1
            player2.points += 3
        else:
            player1.draws += 1
            player2.draws += 1
            player1.points += 1
            player2.points += 1

        # For and Against Goals
        player1.forGoal += int(local)
        player1.againstGoal += int(visit)

        player2.forGoal += int(visit)
        player2.againstGoal += int(local)

        # Goal Difference
        player1.goalDifference = int(player1.forGoal)- int(player1.againstGoal)
        player2.goalDifference = int(player2.forGoal)- int(player2.againstGoal)

        # Played Matches
        player1.played += 1
        player2.played += 1

        # League Info
        league = match.league
        league.played_matches += 1

        player1.save()
        player2.save()
        league.save()

        return HttpResponse(status=200)
    return HttpResponse(status=404)


def register(request):
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'fifa/register.html', {'form': form})


def login_view(request):
    if request.POST:
        user = authenticate(username=request.POST['user'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')

        form = LoginForm(initial={'user': request.POST['user']})
        return render(request, 'fifa/login.html', {'form': form, 'fail': True})
    else:
        form = LoginForm()
    return render(request, 'fifa/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def league_list(request):
    leagues = League.objects.all().order_by('-id')
    paginator = Paginator(leagues, 10)

    page = request.GET.get('page')
    try:
        list = paginator.page(page)
    except PageNotAnInteger:
        list = paginator.page(1)
    except EmptyPage:
        list = paginator.page(paginator.num_pages)

    return render(request, 'fifa/league_list.html', {'leagues': list})


def cover(request):
    return render_to_response('Fifa/cover.html')