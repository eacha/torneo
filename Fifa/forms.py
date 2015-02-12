from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, DateInput, NumberInput
from Fifa.models import League, Player, Week, Team
from django.utils.translation import ugettext, ugettext_lazy as _


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)
    twitter = forms.CharField(required=False)
    first_name = forms.CharField(label=_('first name').title(), max_length=30, required=True)
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput,
                                help_text=_("At least 6 characters."))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'twitter','password1', 'password2')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit = False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
        return user

    def clean_password2(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise ValidationError('Password too short')
        return super(RegistrationForm, self).clean_password2()


class EditPlayerForm(Form):
    first_name = forms.CharField(label=_('first name').title(), max_length=30)
    last_name = forms.CharField(label=_('last name').title(), max_length=30, required=False)
    email = forms.EmailField()
    twitter = forms.CharField(required=False)
    is_active = forms.BooleanField(label=_('active').title(), required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        player = initial.get('player', None)
        super(EditPlayerForm, self).__init__(*args, **kwargs)

        if player:
            self.fields['first_name'].initial = player
            self.fields['last_name'].initial = player.user.last_name
            self.fields['email'].initial = player.user.email
            self.fields['twitter'].initial = player.twitter_account
            self.fields['is_active'].initial = player.user.is_active

        self.fields['first_name'].widget.attrs = {'class': 'form-control'}
        self.fields['last_name'].widget.attrs = {'class': 'form-control'}
        self.fields['email'].widget.attrs = {'class': 'form-control'}
        self.fields['twitter'].widget.attrs = {'class': 'form-control'}


class WeekForm(ModelForm):
    number = forms.IntegerField(widget=NumberInput(attrs={'class': 'form-control'}))
    start = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    finish = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Week
        fields = ['number', 'start', 'finish']


class ResetPasswordForm(SetPasswordForm):

    def clean_new_password2(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 6:
            raise ValidationError('Password too short')
        return super(ResetPasswordForm, self).clean_new_password2()


class LoginForm(Form):
    user = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Usuario',
                                                                        'class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena',
                                                                                'class': 'form-control'}))


class LeagueForm(ModelForm):

    class Meta:
        model = League
        fields = ['name', 'max_players']
        labels = {
            'name': 'Nombre de la Liga',
            'max_players': 'Maximo numero de jugadores'
        }


class TeamSelection(Form):
    CHOICES = (('0', 'Elegir equipo'),)
    selected_team = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        choices = initial.get('selected_team', None)
        super(TeamSelection, self).__init__(*args, **kwargs)
        if choices:
            self.fields['selected_team'].choices = choices


class TeamSelectionData(Form):
    matches_per_week = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    start_week = forms.ModelChoiceField(queryset=Week.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    matches_between = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class InscriptionForm(Form):
    team1 = forms.ModelChoiceField(queryset=Team.objects.all().order_by('name'),
                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                   label='Equipo 1')
    team2 = forms.ModelChoiceField(queryset=Team.objects.all().order_by('name'),
                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                   label='Equipo 2')
    team3 = forms.ModelChoiceField(queryset=Team.objects.all().order_by('name'),
                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                   label='Equipo 3')
