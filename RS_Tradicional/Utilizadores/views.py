# Utilizadores/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection, DatabaseError


def register_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        morada = request.POST.get("morada", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not nome or not email or not nif or not password:
            messages.error(request, "Preenche todos os campos obrigatórios.")
        elif password != password2:
            messages.error(request, "As passwords não coincidem.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        else:
            password_hash = make_password(password)

            try:
                with connection.cursor() as cur:
                    cur.execute(
                        "CALL sp_registar_utilizador_cliente(%s, %s, %s, %s, %s)",
                        [nome, email, password_hash, morada if morada else None, nif],
                    )
            except DatabaseError as e:
                erro = str(e.__cause__ or e)

                if "Já existe um utilizador com esse email" in erro:
                    messages.error(request, "Já existe um utilizador com esse email.")
                elif "Já existe um utilizador com esse NIF" in erro:
                    messages.error(request, "Já existe um utilizador com esse NIF.")
                elif 'Tipo_Utilizador "cliente" não existe' in erro:
                    messages.error(
                        request,
                        "Tipo de utilizador 'cliente' não está configurado na base de dados."
                    )
                else:
                    messages.error(request, f"Ocorreu um erro ao registar: {erro}")
            else:
                messages.success(request, "Registo efetuado com sucesso! Faz login.")
                return redirect("login")

    return render(request, "conta/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        row = None

        try:
            with connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id_utilizador,
                        nome,
                        email,
                        password,
                        morada,
                        nif,
                        id_tipo_utilizador,
                        tipo_designacao
                    FROM fn_get_utilizador_por_email(%s)
                    """,
                    [email],
                )
                row = cur.fetchone()
        except DatabaseError as e:
            messages.error(request, f"Erro ao autenticar: {str(e.__cause__ or e)}")
            row = None

        if not row:
            messages.error(request, "Credenciais inválidas.")
        else:
            (
                id_utilizador,
                nome,
                email_db,
                password_hash,
                morada,
                nif,
                id_tipo_utilizador,
                tipo_designacao,
            ) = row

            # Alguns utilizadores (ex: fornecedor criado por trigger) podem ter password placeholder
            try:
                ok_password = check_password(password, password_hash)
            except ValueError:
                ok_password = False

            if not ok_password:
                messages.error(request, "Credenciais inválidas.")
            else:
                request.session["user_id"] = id_utilizador
                request.session["user_nome"] = nome
                request.session["user_email"] = email_db

                # Guardar tipo sempre consistente em lowercase (resolvido)
                request.session["user_tipo"] = (tipo_designacao or "").lower() or None

                messages.success(request, f"Bem-vindo, {nome}!")
                return redirect("home")

    return render(request, "conta/login.html")


def logout_view(request):
    request.session.flush()
    messages.success(request, "Terminaste sessão com sucesso.")
    return redirect("home")
