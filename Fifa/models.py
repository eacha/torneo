from django.db import models


class League(models.Model):
    name = models.CharField(max_length=100)
    start = models.BooleanField(default=False)
    finish = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    league = models.ForeignKey(League)

    def __unicode__(self):
        return self.name


class Match(models.Model):
    league = models.ForeignKey(League)
    local = models.ForeignKey(Player, related_name='match_locals')
    visit = models.ForeignKey(Player, related_name='match_visits')
    week = models.IntegerField()
    local_score = models.IntegerField()
    visit_score = models.IntegerField()

    def __unicode__(self):
        return self.local.__unicode__() + " - " + self.visit.__unicode__()