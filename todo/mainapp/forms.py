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


class CartProductDescription(forms.ModelForm):
    def __init__(self, product: Product, *args, **kwargs):
        SIZES = []
        for i in range(42, product.max_size + 2, 2):
            SIZES.append((i, str(i)))

        super(CartProductDescription, self).__init__(*args, **kwargs)
        self.fields['size'].widget = forms.Select(choices=tuple(SIZES))
        self.fields['size'].queryset = range(42, product.max_size + 2, 2)


    class Meta:
        model = CartProduct
        fields = ('color', 'size', 'height',
                  'size_of_rud', 'size_of_waist',
                  'size_of_hips')
