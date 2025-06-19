from django.urls import reverse, resolve
from core import views
from django.contrib.auth import views as auth_views

def test_signup_url():
    assert reverse('signup') == '/signup/'
    assert resolve('/signup/').func == views.signup

def test_login_url():
    assert reverse('login') == '/login/'

def test_logout_url():
    assert reverse('logout') == '/logout/'

def test_dashboard_url():
    assert reverse('dashboard') == '/dashboard/'

def test_teacher_management_url():
    assert reverse('teacher_management') == '/teachers/'
