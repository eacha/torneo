from django.db import models
from django.conf import settings


class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    twitter_account = models.CharField(max_length=15)
    # name = models.CharField(max_length=100)
    # team = models.CharField(max_length=100)
    # league = models.ForeignKey(League)

    def __unicode__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    stars = models.DecimalField(max_digits=2, decimal_places=1)

    def __unicode__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=100)
    registration = models.BooleanField(default=True)
    playing = models.BooleanField(default=False)
    players = models.ManyToManyField(Player, through=LeaguePlayer)
    # start = models.BooleanField(default=False)
    # finish = models.BooleanField(default=False)
    played_matches = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=100)

    def __unicode__(self):
        return self.name


class LeaguePlayer(models.Model):
    id_player = models.ForeignKey(Player)
    id_league = models.ForeignKey(League)
    id_team = models.ForeignKey(Team)

    def __unicode__(self):
        return self.id_player.user.name + '-' + self.id_league.name


class Week(models.Model):
    number = models.IntegerField()
    start = models.DateField()
    finish = models.DateField()

    def __unicode__(self):
        return self.number


class Match(models.Model):
    league = models.ForeignKey(League)
    local = models.ForeignKey(Player, related_name='match_locals')
    visit = models.ForeignKey(Player, related_name='match_visits')
    round = models.IntegerField
    week = models.ForeignKey(Week)
    local_score = models.IntegerField()
    visit_score = models.IntegerField()

    def __unicode__(self):
        return self.local.__unicode__() + " - " + self.visit.__unicode__()


class PositionTable(models.Model):
    league = models.ForeignKey(League)
    player = models.ForeignKey(Player)
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
