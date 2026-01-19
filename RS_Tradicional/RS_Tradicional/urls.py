# RS_Tradicional/urls.py
from django.urls import path, include

urlpatterns = [
    path("", include("Core.urls"), name="core"),
    path("conta/", include("Utilizadores.urls"), name="conta"),
]
