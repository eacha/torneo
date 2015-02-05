from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form
from Fifa.models import League, Player, Week
from django.utils.translation import ugettext, ugettext_lazy as _


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)
    twitter = forms.CharField(required=False)
    first_name = forms.CharField(required=True)
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


class ResetPasswordForm(SetPasswordForm):

    def clean_new_password2(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 6:
            raise ValidationError('Password too short')
        return super(ResetPasswordForm, self).clean_new_password2()


class LoginForm(Form):
    user = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Nombre de Usuario'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena'}))


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
