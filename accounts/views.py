from django.shortcuts import render, redirect
from .models import User
from .forms import UserForm, LoginForm
from decimal import Decimal

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def index(request):
    users = User.objects.order_by('id')
    return render(request, "accounts/index.html", {'title': 'Приветствие', 'users': users})


def profile(request):
    name = request.session.get('user_name')
    user = User.objects.filter(name=name).first()
    return render(request, "accounts/profile.html", {'user': user})


def signup(request):
    error = ''
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['user_name'] = user.name
            return redirect('profile')
        else:
            error = 'Неверные данные'

    form = UserForm()
    context = {
        'form': form,
        'error': error
    }
    return render(request, "accounts/signup.html", context)

"""
def login(request):
    error = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        user = User.objects.filter(name=name, password=password).first()

        if user:
            request.session['user_name'] = user.name
            return redirect('profile')
        else:
            error = 'Неверное имя или пароль'

    form = LoginForm()
    context = {
        'form': form,
        'error': error
    }

    return render(request, 'accounts/login.html', context)
"""


def logout(request):
    request.session['user_name'] = None
    return redirect('home')


def google_login(request):
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    scope = "openid email profile https://www.googleapis.com/auth/photoslibrary.readonly"
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scope}"
        "&access_type=offline&prompt=consent"
    )
    return redirect(auth_url)


def google_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('google-login')

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_resp = requests.post(token_url, data=data)
    token_data = token_resp.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    userinfo_resp = requests.get(userinfo_url, headers=headers)
    userinfo = userinfo_resp.json()
    email = userinfo.get('email')
    name = userinfo.get('name', '')

    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email, 'first_name': name}
    )
    login(request, user)

    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    return redirect('photo')


@login_required
def photo(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('google-login')

    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=20'
    resp = requests.get(url, headers=headers)
    data = resp.json()
    media_items = data.get('mediaItems', [])

    return render(request, 'gallery.html', {'media_items': media_items})
