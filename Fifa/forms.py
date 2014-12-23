from django.forms import ModelForm
from Fifa.models import League


class LeagueForm(ModelForm):

    class Meta:
        model = League
        fields = ['name',]