from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from Fifa.models import League, Player, Week


class LeagueForm(ModelForm):

    class Meta:
        model = League
        fields = ['name', 'max_players']
        labels = {
            'name': 'Nombre de la Liga',
            'max_players': 'Maximo numero de jugadores'
        }


# class PlayerForm(ModelForm):
#
#     class Meta:
#         model = Player
#         fields = ['name', 'team']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)
    twitter = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'twitter','password1', 'password2')
        required = ('first_name')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit = False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class LoginForm(Form):
    user = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Nombre de Usuario'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena'}))


class TeamSelection(Form):
    CHOICES = (('0', 'Elegir equipo'),)
    selected_team = forms.ChoiceField(choices=CHOICES)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        choices = initial.get('selected_team', None)
        super(TeamSelection, self).__init__(*args, **kwargs)
        if choices:
            self.fields['selected_team'].choices = choices


class TeamSelectionDates(Form):
    matches_per_week = forms.IntegerField()
    start_week = forms.ModelChoiceField(queryset=Week.objects.all())
