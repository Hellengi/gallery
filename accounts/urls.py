from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='home'),
    path('profile', views.profile, name='profile'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    path('google/login/', views.google_login, name='google-login'),
    path('google/callback/', views.google_callback, name='google-callback'),
    path('photos/', views.photo, name='photo'),
]
