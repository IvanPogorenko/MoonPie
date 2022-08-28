from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.views.generic import CreateView

from .models import *


class UserRegister(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'fadeIn second', 'placeholder': 'Логин'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'fadeIn third', 'placeholder': 'Почта'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'fadeIn third', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'fadeIn third', 'placeholder': 'Повторите пароль'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class Authentication(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'fadeIn second', 'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'fadeIn third', 'placeholder': 'Пароль'}))


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'comment'
        )
