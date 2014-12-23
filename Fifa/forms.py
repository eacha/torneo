from django.forms import ModelForm
from Fifa.models import League, Player


class LeagueForm(ModelForm):

    class Meta:
        model = League
        fields = ['name']


class PlayerForm(ModelForm):

    class Meta:
        model = Player
        fields = ['name', 'team']