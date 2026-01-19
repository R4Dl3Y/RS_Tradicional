# Utilizadores/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from .models import Utilizador, TipoUtilizador


def register_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        morada = request.POST.get("morada", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        # validações básicas
        if not nome or not email or not nif or not password:
            messages.error(request, "Preenche todos os campos obrigatórios.")
        elif password != password2:
            messages.error(request, "As passwords não coincidem.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        elif Utilizador.objects.filter(email=email).exists():
            messages.error(request, "Já existe um utilizador com esse email.")
        else:
            # tentar obter o tipo "cliente" (não dá erro se não existir, fica None)
            tipo_cliente = TipoUtilizador.objects.filter(
                designacao__iexact="cliente"
            ).first()

            Utilizador.objects.create(
                nome=nome,
                email=email,
                nif=nif,
                morada=morada if morada else None,
                password=make_password(password),
                id_tipo_utilizador=tipo_cliente,  # fica NULL se tipo_cliente for None
            )

            messages.success(request, "Registo efetuado com sucesso! Faz login.")
            return redirect("login")

    # paths dos templates como tu já estás a usar
    return render(request, "conta/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        try:
            user = Utilizador.objects.get(email=email)
        except Utilizador.DoesNotExist:
            user = None

        if user is None or not check_password(password, user.password):
            messages.error(request, "Credenciais inválidas.")
        else:
            # guardar dados do utilizador na sessão
            request.session["user_id"] = user.id_utilizador
            request.session["user_nome"] = user.nome
            request.session["user_email"] = user.email

            # se quiseres guardar o tipo também:
            if user.id_tipo_utilizador:
                request.session["user_tipo"] = user.id_tipo_utilizador.designacao
            else:
                request.session["user_tipo"] = None

            messages.success(request, f"Bem-vindo, {user.nome}!")
            return redirect("home")

    return render(request, "conta/login.html")


def logout_view(request):
    request.session.flush()
    messages.success(request, "Terminaste sessão com sucesso.")
    return redirect("home")
