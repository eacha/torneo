from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from math import floor
from Fifa.forms import LeagueForm, RegistrationForm, LoginForm, TeamSelection, TeamSelectionDates
from Fifa.models import League, Player, Match, PositionTable, RegistrationLeague, LeaguePlayer, Team, Week
from Fix.Fixture import Fixture


def login_view(request):
    if request.POST:
        user = authenticate(username=request.POST['user'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                url = reverse('Fifa.views.inicio')
                return HttpResponseRedirect(url)

        form = LoginForm(initial={'user': request.POST['user']})
        return render(request, 'fifa/login.html', {'form': form, 'fail': True})
    else:
        form = LoginForm()
    return render(request, 'fifa/login.html', {'form': form})


def logout_view(request):
    logout(request)
    url = reverse('Fifa.views.cover')
    return HttpResponseRedirect(url)


def register(request):
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            player = Player(user=user, twitter_account=form.cleaned_data['twitter'])
            player.save()
            url = reverse('Fifa.views.login_view')
            return HttpResponseRedirect(url)

    form = RegistrationForm()
    return render(request, 'Fifa/register.html', {'form': form})


def cover(request):
    data = {'form': LoginForm()}
    c = RequestContext(request, data)
    return render_to_response('Fifa/cover.html', c)


@staff_member_required
def administration(request):
    leagues = League.objects.all()
    data = {'leagues': leagues}
    c = RequestContext(request, data)
    return render_to_response('fifa/administration.html', c)


@staff_member_required
def admin_leagues(request):
    leagues = League.objects.all()
    data = {'leagues': leagues}
    c = RequestContext(request, data)
    return render_to_response('Fifa/admin_leagues.html', c)


@staff_member_required
def new_league(request):
    if request.POST:
        form = LeagueForm(request.POST)
        if form.is_valid():
            form.save()
            leagues = League.objects.all()
            data = {'leagues': leagues}
            c = RequestContext(request, data)
            return render_to_response('Fifa/admin_leagues.html', c)

    form = LeagueForm()
    return render(request, 'fifa/league_form.html', {'form': form})


@staff_member_required
def edit_league(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    if league.registration:
        registers = RegistrationLeague.objects.filter(league=league)
        TeamSelectionSet = formset_factory(TeamSelection, extra=0)

        initial_data = []
        for register in registers:
            choices = {'selected_team': [('0', 'Elegir equipo'),
                                         (str(register.team1.id), register.team1.name),
                                         (str(register.team2.id), register.team2.name),
                                         (str(register.team3.id), register.team3.name)]}
            initial_data += [choices]

        if request.POST:
            forms = TeamSelectionSet(request.POST, request.FILES, initial=initial_data)
            form_dates = TeamSelectionDates(request.POST)
            if forms.is_valid() and form_dates.is_valid():
                for form, register in zip(forms, registers):
                    team = Team.objects.get(pk=int(form.cleaned_data['selected_team']))
                    inscription = LeaguePlayer(player=register.player,
                                               league=league,
                                               team=team)
                    inscription.save()
                start_week = form_dates.cleaned_data['start_week']
                generate_match(league,form_dates.cleaned_data['matches_per_week'], start_week)

                url = reverse('Fifa.views.edit_league')
                return HttpResponseRedirect(url)

        forms = TeamSelectionSet(initial=initial_data)
        form_dates = TeamSelectionDates()
        leagues = League.objects.all()
        data = {'data': zip(registers, forms),
                'league': league,
                'form': forms,
                'form_dates': form_dates,
                'leagues': leagues}
        c = RequestContext(request, data)
        return render_to_response('Fifa/edit_league_registration.html', c)
    else:
        league = get_object_or_404(League, id=league_id)
        players = LeaguePlayer.objects.filter(league=league)
        # if league.playing:
        leagues = League.objects.all()
        matches = Match.objects.filter(league=league).order_by('week')
        matches_per_week = floor(league.players.count() / 2)

        paginator = Paginator(matches, matches_per_week)
        page = request.GET.get('page')
        try:
            matches = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            matches = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            matches = paginator.page(paginator.num_pages)

        data = {'league': league,
                'players': players,
                'matches': matches,
                'leagues': leagues,
                'fecha': matches.object_list[0].round}
        return render(request, 'fifa/league_details.html', data)
        # return render(request, 'fifa/league_details.html', {'league': league, 'players': players})

@staff_member_required
def end_league(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    league.playing = False
    league.save()
    return edit_league(request, league_id)




# def new_player(request, league_id):
#     league = get_object_or_404(League, id=league_id)
#     if request.POST:
#         form = PlayerForm(request.POST)
#         if form.is_valid():
#             player = form.save(commit=False)
#             player.league = league
#             player.save()
#
#             return HttpResponseRedirect('/')
#     else:
#         form = PlayerForm()
#     return render(request, 'fifa/player_form.html', {'form': form, 'league': league})


def generate_match(league, matches_per_week, start_week):
    if league.registration:
        players = league.players.all()
        # Created Position Table
        for player in players:
            position = PositionTable(league=league,
                                     player=player)
            position.save()
        # Created Matchs
        fix = Fixture(list(players))
        fixture = fix.generate()
        counter = 1
        week = start_week
        for round in fixture:
            for match in round:
                element = Match(league=league,
                                local=match[0],
                                visit=match[1],
                                round=counter,
                                week=week,
                                local_score=-1,
                                visit_score=-1)
                element.save()
            counter += 1
            if counter % matches_per_week == 1:
                next_week = week.number + 1
                week = Week.objects.get(number=next_week)

        # set league properties
        matches = Match.objects.filter(league=league).count()
        league.registration = False
        league.playing = True
        league.total_matches = matches
        league.save()



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
        leagues = League.objects.all()
        data = {'league': league,
                'players': players,
                'matches': matches,
                'leagues': leagues}
        return render(request, 'fifa/league_details.html', data)
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
        player1 = PositionTable.objects.get(league=match.league, player=match.local)
        player2 = PositionTable.objects.get(league=match.league, player=match.visit)

        #Editing old result
        if match.local_score != -1:
            old_local = match.local_score
            old_visit = match.visit_score

            if old_local > old_visit:
                player1.wins -= 1
                player2.losses -= 1
                player1.points -= 3
            elif old_local < old_visit:
                player1.losses -= 1
                player2.wins -= 1
                player2.points -= 3
            else:
                player1.draws -= 1
                player2.draws -= 1
                player1.points -= 1
                player2.points -= 1

            # For and Against Goals
            player1.forGoal -= int(old_local)
            player1.againstGoal -= int(old_visit)

            player2.forGoal -= int(old_visit)
            player2.againstGoal -= int(old_local)

            # Goal Difference
            player1.goalDifference = int(player1.forGoal) - int(player1.againstGoal)
            player2.goalDifference = int(player2.forGoal) - int(player2.againstGoal)

            # Played Matches
            player1.played -= 1
            player2.played -= 1

            # League Info
            league = match.league
            league.played_matches -= 1

        local = int(request.POST.get("local", ""))
        visit = int(request.POST.get("visit", ""))
        match.local_score = local
        match.visit_score = visit
        match.save()

        # Wins, Losses, Draws and Points
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

        matches = Match.objects.filter(league=league).order_by('week')
        matches_per_week = floor(league.players.count() / 2)
        paginator = Paginator(matches, matches_per_week)
        page = request.GET.get('page')

        try:
            matches = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            matches = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            matches = paginator.page(paginator.num_pages)

        data = {'matches': matches}
        c = RequestContext(request, data)
        return render_to_response('Fifa/matches.html', c)
    return HttpResponse(status=404)











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





@login_required()
def inicio(request):
    leagues = League.objects.all()
    data = {'leagues': leagues}
    c = RequestContext(request, data)
    return render_to_response('Fifa/inicio.html', c)
