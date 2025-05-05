from .models import User
from django.forms import ModelForm, TextInput, Form, CharField, PasswordInput


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["name", "password"]
        widgets = {
            "name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя, оно должно быть уникальным'
            }),
            "password": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль'
            }),
        }


class LoginForm(Form):
    name = CharField(
        label='Имя',
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    password = CharField(
        label='Пароль',
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
