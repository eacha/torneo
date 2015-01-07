from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from Fifa.models import League, Player


class LeagueForm(ModelForm):

    class Meta:
        model = League
        fields = ['name']


class PlayerForm(ModelForm):

    class Meta:
        model = Player
        fields = ['name', 'team']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit = False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class LoginForm(Form):
    user = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())