from datetime import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import formset_factory, modelformset_factory
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from math import floor
from Fifa.forms import LeagueForm, RegistrationForm, LoginForm, TeamSelection, TeamSelectionData, EditPlayerForm, \
    WeekForm, InscriptionForm
from Fifa.models import League, Player, Match, PositionTable, RegistrationLeague, LeaguePlayer, Team, Week
from Fix.Fixture import Fixture


def login_view(request):
    if request.POST:
        user = authenticate(username=request.POST['user'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                url = reverse('Fifa.views.index')
                return HttpResponseRedirect(url)

        form = LoginForm(initial={'user': request.POST['user']})
        return render(request, 'Fifa/login.html', {'form': form, 'fail': True})
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
        else:
            return render(request, 'Fifa/register.html', {'form': form})

    form = RegistrationForm()
    return render(request, 'Fifa/register.html', {'form': form})


def cover(request):
    if request.user.is_authenticated():
        return index(request)

    data = {'form': LoginForm()}
    c = RequestContext(request, data)
    return render_to_response('Fifa/cover.html', c)


@staff_member_required
def administration(request):
    leagues = League.objects.all()
    data = {'leagues': leagues}
    c = RequestContext(request, data)
    return render_to_response('Fifa/administration.html', c)


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
            form_dates = TeamSelectionData(request.POST)
            if forms.is_valid() and form_dates.is_valid():
                for form, register in zip(forms, registers):
                    team = Team.objects.get(pk=int(form.cleaned_data['selected_team']))
                    inscription = LeaguePlayer(player=register.player,
                                               league=league,
                                               team=team)
                    inscription.save()
                start_week = form_dates.cleaned_data['start_week']
                generate_match(league,
                               form_dates.cleaned_data['matches_per_week'],
                               start_week,
                               form_dates.cleaned_data['matches_between'])

                url = reverse('Fifa.views.edit_league', kwargs={'league_id': league_id})
                return HttpResponseRedirect(url)

        forms = TeamSelectionSet(initial=initial_data)
        form_dates = TeamSelectionData()
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
        return render(request, 'fifa/edit_league_playing.html', data)


@staff_member_required
def end_league(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    league.playing = False
    league.save()
    return edit_league(request, league_id)

@staff_member_required
def admin_players(request):
    leagues = League.objects.all()
    players = Player.objects.all()
    data = {'leagues': leagues,
            'players': players}
    c = RequestContext(request, data)
    return render_to_response('Fifa/admin_players.html', c)


@staff_member_required
def edit_player(request, player_id):
    leagues = League.objects.all()
    player = get_object_or_404(Player, pk=player_id)
    if request.POST:
        form = EditPlayerForm(request.POST)
        if form.is_valid():
            player.user.first_name = form.cleaned_data['first_name']
            player.user.last_name = form.cleaned_data['last_name']
            player.user.email = form.cleaned_data['email']
            player.twitter_account = form.cleaned_data['twitter']
            player.user.is_active = form.cleaned_data['is_active']
            player.user.save()
            player.save()

    data = {'leagues': leagues,
            'player': player,
            'form': EditPlayerForm(initial={'player': player})}
    c = RequestContext(request, data)
    return render_to_response('Fifa/edit_players.html', c)


@staff_member_required
def admin_weeks(request):
    leagues = League.objects.all()
    weeks = Week.objects.all()
    WeekFormSet = modelformset_factory(Week, form=WeekForm)
    if request.POST:
        forms = WeekFormSet(request.POST)
        if forms.is_valid():
            forms.save()


    forms = WeekFormSet()
    data = {'leagues': leagues,
            'forms': forms}
    c = RequestContext(request, data)
    return render_to_response('Fifa/admin_weeks.html', c)


def generate_match(league, matches_per_week, start_week, matches_between):
    if league.registration:
        players = league.players.all()
        # Created Position Table
        for player in players:
            position = PositionTable(league=league,
                                     player=player)
            position.save()
        # Created Matchs
        fix = Fixture(list(players), games=matches_between)
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
        match.played = True
        match.played_date = datetime.now()
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

        data = {'matches': matches,
                'league': league}
        c = RequestContext(request, data)
        return render_to_response('Fifa/matches.html', c)
    return HttpResponse(status=404)


@login_required()
def index(request):
    leagues = League.objects.all()
    player = Player.objects.get(user=request.user)
    date = datetime.today()
    week = Week.objects.get(Q(start__lt=date) & Q(finish__gt=date))

    week_matches = Match.objects.filter((Q(visit=player) | Q(local=player))
                                        & Q(week=week)
                                        & Q(league__playing=True))

    late_matches = Match.objects.filter((Q(visit=player) | Q(local=player))
                                        & Q(week__lt=week) & Q(played=False)
                                        & Q(league__playing=True))

    recent_matches = Match.objects.filter(played=True).order_by('-played_date')[0:4]

    matches = []
    for match in week_matches:
        if player == match.local:
            rival = match.visit
            score = ""
            if match.played:
                score = str(match.local_score) + ' - ' + str(match.visit_score)

            if not match.played:
                result = 'panel-info'
            elif match.local_score > match.visit_score:
                result = 'panel-success'
            elif match.local_score < match.visit_score:
                result = 'panel-danger'
            else:
                result = 'panel-warning'
        else:
            rival = match.local

            score = ""
            if match.played:
                score = str(match.visit_score) + ' - ' + str(match.local_score)

            if not match.played:
                result = 'panel-default'
            elif match.local_score < match.visit_score:
                result = 'panel-success'
            elif match.local_score > match.visit_score:
                result = 'panel-danger'
            else:
                result = 'panel-warning'

        match_data = [rival, score, result]
        matches += [match_data]

    late = []
    for match in late_matches:
        if player == match.local:
            rival = match.visit
        else:
            rival = match.local

        late += [rival]

    data = {'leagues': leagues,
            'matches_week': matches,
            'late': late,
            'recents': recent_matches
    }
    c = RequestContext(request, data)
    return render_to_response('Fifa/inicio.html', c)


@login_required
def inscription(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    player = Player.objects.get(user=request.user)
    if request.POST:
        form = InscriptionForm(request.POST)
        if form.is_valid():
            try:
                registration = RegistrationLeague.objects.get(player=player, league=league)
            except RegistrationLeague.DoesNotExist:
                registration = RegistrationLeague()

            registration.league = league
            registration.player = player
            registration.team1 = form.cleaned_data['team1']
            registration.team2 = form.cleaned_data['team2']
            registration.team3 = form.cleaned_data['team3']
            registration.save()

            leagues = League.objects.all()
            data = {'leagues': leagues,
                    'league': league,
                    'form': form,
                    'ok': True
            }
            c = RequestContext(request, data)
            return render_to_response('Fifa/inscription.html', c)

    try:
        pre = RegistrationLeague.objects.get(player=player, league=league)
        form = InscriptionForm(initial = {'team1': pre.team1.pk,
                                          'team2': pre.team2.pk,
                                          'team3': pre.team3.pk})
        previous = True
    except RegistrationLeague.DoesNotExist:
        form = InscriptionForm()
        previous = False

    leagues = League.objects.all()
    data = {'leagues': leagues,
            'league': league,
            'form': form,
            'previous': previous
    }
    c = RequestContext(request, data)
    return render_to_response('Fifa/inscription.html', c)


def league_details(request, league_id):
    league = get_object_or_404(League, id=league_id)
    players = LeaguePlayer.objects.filter(league=league)
    position_table = PositionTable.objects.filter(league=league)
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
            'fecha': matches.object_list[0].round,
            'position_table': position_table}
    return data

@login_required
def league_details_matches(request, league_id):
    data = league_details(request, league_id)
    data['matches_page'] = True
    c = RequestContext(request, data)
    return render_to_response('Fifa/league_details.html', c)


@login_required
def league_details_positions(request, league_id):
    data = league_details(request, league_id)
    data['positions_page'] = True
    c = RequestContext(request, data)
    return render_to_response('Fifa/league_details.html', c)

