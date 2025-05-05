from urllib.parse import urlencode

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def index(request):
    return render(request, "accounts/index.html")


def google_login(request):
    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile https://www.googleapis.com/auth/photoslibrary.readonly",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
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

    print("ACCESS TOKEN:", access_token)

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
    print(resp)
    print(data)
    print(media_items)
    url = 'https://photoslibrary.googleapis.com/v1/albums'
    resp = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
    print(resp.status_code)
    print(resp.json())

    return render(request, 'accounts/gallery.html', {'media_items': media_items})
