# Utilizadores/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("registo/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
