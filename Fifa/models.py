from django.db import models
from django.conf import settings


class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    twitter_account = models.CharField(max_length=15)

    def __unicode__(self):
        return self.user.first_name

    def get_twitter(self):
        if self.twitter_account != "":
            return '@' + self.twitter_account
        return self.__unicode__()


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=100)
    registration = models.BooleanField(default=True)
    playing = models.BooleanField(default=False)
    players = models.ManyToManyField(Player, through='LeaguePlayer')
    max_players = models.IntegerField(default=16)
    played_matches = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=100)

    def __unicode__(self):
        return self.name

    def get_progress(self):
        perc = (self.played_matches * 100) / self.total_matches
        return perc


class LeaguePlayer(models.Model):
    player = models.ForeignKey(Player)
    league = models.ForeignKey(League)
    team = models.ForeignKey(Team, null=True)

    def __unicode__(self):
        return self.player.user.first_name + '-' + self.league.name


class Week(models.Model):
    number = models.IntegerField()
    start = models.DateField()
    finish = models.DateField()

    def __unicode__(self):
        return str(self.number)

    class Meta:
        ordering = ['number']


class Match(models.Model):
    league = models.ForeignKey(League)
    local = models.ForeignKey(Player, related_name='match_locals')
    visit = models.ForeignKey(Player, related_name='match_visits')
    round = models.IntegerField()
    week = models.ForeignKey(Week)
    local_score = models.IntegerField()
    visit_score = models.IntegerField()
    played = models.BooleanField(default=False)
    played_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.league.__unicode__() + ": " + self.local.__unicode__() + " - " + self.visit.__unicode__()


class PositionTable(models.Model):
    league = models.ForeignKey(League)
    player = models.ForeignKey(Player)
    team = models.ForeignKey(Team)
    played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    forGoal = models.IntegerField(default=0)
    againstGoal = models.IntegerField(default=0)
    goalDifference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        ordering = ['-points', '-goalDifference', '-forGoal']

    def __unicode__(self):
        return self.league.__unicode__() + " " + self.player.__unicode__()


class RegistrationLeague(models.Model):
    player = models.ForeignKey(Player)
    league = models.ForeignKey(League)
    team1 = models.ForeignKey(Team, related_name='team1')
    team2 = models.ForeignKey(Team, related_name='team2')
    team3 = models.ForeignKey(Team, related_name='team3')

    class Meta:
        unique_together = (('player', 'league'),)

    def __unicode__(self):
        return self.league.__unicode__() + ' - ' + self.player.__unicode__()