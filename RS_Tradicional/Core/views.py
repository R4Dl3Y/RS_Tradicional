# Core/views.py
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from Produtos.models import Produto, TipoProduto, Fornecedor
from Utilizadores.models import Utilizador, TipoUtilizador
from Encomendas.models import Encomenda, EncomendaProduto
from Noticias.models import Noticia, TipoNoticia


def _require_admin(request):
    """
    Verifica se o utilizador logado é admin ou gestor.
    """
    user_tipo = request.session.get("user_tipo")

    if not user_tipo or user_tipo.lower() not in ("admin", "gestor"):
        messages.error(request, "Não tens permissões para aceder a esta área.")
        return False
    return True

def _require_admin_only(request):
    """
    Apenas ADMIN pode gerir utilizadores.
    """
    user_tipo = request.session.get("user_tipo")

    if not user_tipo or user_tipo.lower() != "admin":
        messages.error(request, "Apenas administradores podem gerir utilizadores.")
        return False
    return True


def home(request):
    context = {
        "welcome_message": "Bem-vindo à RS Tradicional!",
    }
    return render(request, "core/home.html", context)


def admin_dashboard(request):
    if not _require_admin(request):
        return redirect("home")

    context = {
        "titulo": "Painel de Administração",
    }
    return render(request, "admin/admin_dashboard.html", context)


# ===============================
#   ADMIN – PRODUTOS
# ===============================

def admin_product_list(request):
    if not _require_admin(request):
        return redirect("home")

    produtos = (
        Produto.objects
        .select_related("id_tipo_produto", "id_fornecedor")
        .order_by("id_produto")
    )

    context = {
        "produtos": produtos,
    }
    return render(request, "admin/produtos/list.html", context)


def admin_product_create(request):
    if not _require_admin(request):
        return redirect("home")

    tipos = TipoProduto.objects.all().order_by("designacao")
    fornecedores = Fornecedor.objects.all().order_by("nome")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        preco_str = request.POST.get("preco", "").replace(",", ".").strip()
        stock_str = request.POST.get("stock", "").strip()
        tipo_id = request.POST.get("tipo_produto") or None
        fornecedor_id = request.POST.get("fornecedor") or None

        estado = request.POST.get("estado_produto", "").strip() or "Ativo"
        is_approved = request.POST.get("is_approved") == "on"

        # validações básicas
        if not nome or not preco_str or not stock_str:
            messages.error(request, "Preenche pelo menos nome, preço e stock.")
        else:
            try:
                preco = Decimal(preco_str)
                if preco < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                messages.error(request, "Preço inválido.")
                preco = None

            try:
                stock = int(stock_str)
                if stock < 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Stock inválido.")
                stock = None

            if preco is not None and stock is not None:
                tipo_obj = TipoProduto.objects.filter(pk=tipo_id).first() if tipo_id else None
                fornecedor_obj = Fornecedor.objects.filter(pk=fornecedor_id).first() if fornecedor_id else None

                Produto.objects.create(
                    nome=nome,
                    descricao=descricao or None,
                    preco=preco,
                    stock=stock,
                    is_approved=is_approved,
                    estado_produto=estado,
                    id_tipo_produto=tipo_obj,
                    id_fornecedor=fornecedor_obj,
                )
                messages.success(request, "Produto criado com sucesso.")
                return redirect("admin_product_list")

    context = {
        "tipos": tipos,
        "fornecedores": fornecedores,
        "acao": "Criar",
    }
    return render(request, "admin/produtos/form.html", context)


def admin_product_edit(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    produto = get_object_or_404(Produto, pk=produto_id)
    tipos = TipoProduto.objects.all().order_by("designacao")
    fornecedores = Fornecedor.objects.all().order_by("nome")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        preco_str = request.POST.get("preco", "").replace(",", ".").strip()
        stock_str = request.POST.get("stock", "").strip()
        tipo_id = request.POST.get("tipo_produto") or None
        fornecedor_id = request.POST.get("fornecedor") or None

        estado = request.POST.get("estado_produto", "").strip() or "Ativo"
        is_approved = request.POST.get("is_approved") == "on"

        if not nome or not preco_str or not stock_str:
            messages.error(request, "Preenche pelo menos nome, preço e stock.")
        else:
            try:
                preco = Decimal(preco_str)
                if preco < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                messages.error(request, "Preço inválido.")
                preco = None

            try:
                stock = int(stock_str)
                if stock < 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Stock inválido.")
                stock = None

            if preco is not None and stock is not None:
                produto.nome = nome
                produto.descricao = descricao or None
                produto.preco = preco
                produto.stock = stock
                produto.estado_produto = estado
                produto.is_approved = is_approved
                produto.id_tipo_produto = (
                    TipoProduto.objects.filter(pk=tipo_id).first()
                    if tipo_id else None
                )
                produto.id_fornecedor = (
                    Fornecedor.objects.filter(pk=fornecedor_id).first()
                    if fornecedor_id else None
                )
                produto.save()
                messages.success(request, "Produto atualizado com sucesso.")
                return redirect("admin_product_list")

    context = {
        "produto": produto,
        "tipos": tipos,
        "fornecedores": fornecedores,
        "acao": "Editar",
    }
    return render(request, "admin/produtos/form.html", context)


def admin_product_delete(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == "POST":
        nome = produto.nome
        produto.delete()
        messages.success(request, f"Produto '{nome}' removido com sucesso.")
        return redirect("admin_product_list")

    context = {
        "produto": produto,
    }
    return render(request, "admin/produtos/confirm_delete.html", context)

# ===============================
#   ADMIN – TIPOS DE PRODUTO
# ===============================

def admin_tipo_produto_list(request):
    if not _require_admin(request):
        return redirect("home")

    tipos = TipoProduto.objects.order_by("designacao")

    context = {
        "tipos": tipos,
    }
    return render(request, "admin/tipos_produto/list.html", context)


def admin_tipo_produto_create(request):
    if not _require_admin(request):
        return redirect("home")

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            # impedir duplicados simples
            if TipoProduto.objects.filter(designacao__iexact=designacao).exists():
                messages.error(request, "Já existe um tipo de produto com essa designação.")
            else:
                TipoProduto.objects.create(designacao=designacao)
                messages.success(request, "Tipo de produto criado com sucesso.")
                return redirect("admin_tipo_produto_list")

    context = {
        "acao": "Criar",
    }
    return render(request, "admin/tipos_produto/form.html", context)


def admin_tipo_produto_edit(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    tipo = get_object_or_404(TipoProduto, pk=tipo_id)

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            # permitir manter o mesmo nome, mas evitar colidir com outro
            if TipoProduto.objects.filter(
                designacao__iexact=designacao
            ).exclude(pk=tipo_id).exists():
                messages.error(request, "Já existe outro tipo de produto com essa designação.")
            else:
                tipo.designacao = designacao
                tipo.save()
                messages.success(request, "Tipo de produto atualizado com sucesso.")
                return redirect("admin_tipo_produto_list")

    context = {
        "acao": "Editar",
        "tipo": tipo,
    }
    return render(request, "admin/tipos_produto/form.html", context)


def admin_tipo_produto_delete(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    tipo = get_object_or_404(TipoProduto, pk=tipo_id)

    if request.method == "POST":
        nome = tipo.designacao
        tipo.delete()
        messages.success(request, f"Tipo de produto '{nome}' removido com sucesso.")
        return redirect("admin_tipo_produto_list")

    context = {
        "tipo": tipo,
    }
    return render(request, "admin/tipos_produto/confirm_delete.html", context)

# ===============================
#   ADMIN – FORNECEDORES
# ===============================

def admin_fornecedor_list(request):
    if not _require_admin(request):
        return redirect("home")

    fornecedores = Fornecedor.objects.order_by("nome")

    context = {
        "fornecedores": fornecedores,
    }
    return render(request, "admin/fornecedores/list.html", context)


def admin_fornecedor_create(request):
    if not _require_admin(request):
        return redirect("home")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        contacto = request.POST.get("contacto", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        is_singular_str = request.POST.get("is_singular", "on")  # default: singular
        morada = request.POST.get("morada", "").strip()
        imagem = request.POST.get("imagem_fornecedor", "").strip()

        is_singular = is_singular_str == "on"

        # validações simples
        if not nome or not contacto or not email or not nif:
            messages.error(request, "Preenche todos os campos obrigatórios.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        elif (not is_singular) and not morada:
            messages.error(request, "Para fornecedores não singulares, a morada é obrigatória.")
        else:
            Fornecedor.objects.create(
                nome=nome,
                contacto=contacto,
                email=email,
                nif=nif,
                isSingular=is_singular,
                morada=morada if morada else None,
                imagem_fornecedor=imagem if imagem else None,
            )
            messages.success(request, "Fornecedor criado com sucesso.")
            return redirect("admin_fornecedor_list")

    context = {
        "acao": "Criar",
    }
    return render(request, "admin/fornecedores/form.html", context)


def admin_fornecedor_edit(request, fornecedor_id):
    if not _require_admin(request):
        return redirect("home")

    fornecedor = get_object_or_404(Fornecedor, pk=fornecedor_id)

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        contacto = request.POST.get("contacto", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        is_singular_str = request.POST.get("is_singular", "")
        morada = request.POST.get("morada", "").strip()
        imagem = request.POST.get("imagem_fornecedor", "").strip()

        is_singular = is_singular_str == "on"

        if not nome or not contacto or not email or not nif:
            messages.error(request, "Preenche todos os campos obrigatórios.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        elif (not is_singular) and not morada:
            messages.error(request, "Para fornecedores não singulares, a morada é obrigatória.")
        else:
            fornecedor.nome = nome
            fornecedor.contacto = contacto
            fornecedor.email = email
            fornecedor.nif = nif
            fornecedor.isSingular = is_singular
            fornecedor.morada = morada if morada else None
            fornecedor.imagem_fornecedor = imagem if imagem else None
            fornecedor.save()

            messages.success(request, "Fornecedor atualizado com sucesso.")
            return redirect("admin_fornecedor_list")

    context = {
        "acao": "Editar",
        "fornecedor": fornecedor,
    }
    return render(request, "admin/fornecedores/form.html", context)


def admin_fornecedor_delete(request, fornecedor_id):
    if not _require_admin(request):
        return redirect("home")

    fornecedor = get_object_or_404(Fornecedor, pk=fornecedor_id)

    if request.method == "POST":
        nome = fornecedor.nome
        fornecedor.delete()
        messages.success(request, f"Fornecedor '{nome}' removido com sucesso.")
        return redirect("admin_fornecedor_list")

    context = {
        "fornecedor": fornecedor,
    }
    return render(request, "admin/fornecedores/confirm_delete.html", context)

# ===============================
#   FORNECEDOR – SUBMETER PRODUTO
# ===============================

def fornecedor_product_create(request):
    # 1) Verificar se o utilizador está autenticado como "Fornecedor"
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if user_tipo != "fornecedor":
        messages.error(request, "Apenas utilizadores do tipo Fornecedor podem submeter produtos.")
        return redirect("home")

    # 2) Encontrar o fornecedor associado ao email do utilizador
    user_email = request.session.get("user_email")
    fornecedor = Fornecedor.objects.filter(email=user_email).first()

    if not fornecedor:
        messages.error(
            request,
            "Não foi encontrado nenhum fornecedor associado ao teu email. "
            "Contacta um administrador."
        )
        return redirect("home")

    tipos = TipoProduto.objects.all().order_by("designacao")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        preco_str = request.POST.get("preco", "").replace(",", ".").strip()
        stock_str = request.POST.get("stock", "").strip()
        tipo_id = request.POST.get("tipo_produto") or None

        # validações básicas
        if not nome or not preco_str or not stock_str:
            messages.error(request, "Preenche pelo menos nome, preço e stock.")
        else:
            try:
                preco = Decimal(preco_str)
                if preco < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                messages.error(request, "Preço inválido.")
                preco = None

            try:
                stock = int(stock_str)
                if stock < 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Stock inválido.")
                stock = None

            if preco is not None and stock is not None:
                tipo_obj = TipoProduto.objects.filter(pk=tipo_id).first() if tipo_id else None

                Produto.objects.create(
                    nome=nome,
                    descricao=descricao or None,
                    preco=preco,
                    stock=stock,
                    is_approved=False,             # 👈 Sempre pendente
                    estado_produto="Pendente",     # 👈 Estado inicial
                    id_tipo_produto=tipo_obj,
                    id_fornecedor=fornecedor,
                )
                messages.success(
                    request,
                    "Produto submetido com sucesso. Aguarda aprovação de um administrador/gestor."
                )
                return redirect("home")  # ou uma página "minha lista de produtos"

    context = {
        "tipos": tipos,
        "fornecedor": fornecedor,
    }
    return render(request, "fornecedor/produtos/form.html", context)

# ===============================
#   FORNECEDOR – OS MEUS PRODUTOS
# ===============================

def fornecedor_product_list(request):
    # só fornecedores
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if user_tipo != "fornecedor":
        messages.error(request, "Apenas utilizadores do tipo Fornecedor podem aceder a esta área.")
        return redirect("home")

    user_email = request.session.get("user_email")
    fornecedor = Fornecedor.objects.filter(email=user_email).first()

    if not fornecedor:
        messages.error(
            request,
            "Não foi encontrado nenhum fornecedor associado ao teu email. "
            "Contacta um administrador."
        )
        return redirect("home")

    produtos = (
        Produto.objects
        .filter(id_fornecedor=fornecedor)
        .select_related("id_tipo_produto")
        .order_by("id_produto")
    )

    context = {
        "fornecedor": fornecedor,
        "produtos": produtos,
    }
    return render(request, "fornecedor/produtos/list.html", context)

# ===============================
#   ADMIN – TIPOS DE UTILIZADOR
# ===============================

def admin_tipo_utilizador_list(request):
    if not _require_admin(request):
        return redirect("home")

    tipos = TipoUtilizador.objects.order_by("designacao")

    context = {
        "tipos": tipos,
    }
    return render(request, "admin/tipos_utilizador/list.html", context)


def admin_tipo_utilizador_create(request):
    if not _require_admin(request):
        return redirect("home")

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            if TipoUtilizador.objects.filter(designacao__iexact=designacao).exists():
                messages.error(request, "Já existe um tipo de utilizador com essa designação.")
            else:
                TipoUtilizador.objects.create(designacao=designacao)
                messages.success(request, "Tipo de utilizador criado com sucesso.")
                return redirect("admin_tipo_utilizador_list")

    context = {
        "acao": "Criar",
    }
    return render(request, "admin/tipos_utilizador/form.html", context)


def admin_tipo_utilizador_edit(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    tipo = get_object_or_404(TipoUtilizador, pk=tipo_id)

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            if TipoUtilizador.objects.filter(
                designacao__iexact=designacao
            ).exclude(pk=tipo_id).exists():
                messages.error(request, "Já existe outro tipo de utilizador com essa designação.")
            else:
                tipo.designacao = designacao
                tipo.save()
                messages.success(request, "Tipo de utilizador atualizado com sucesso.")
                return redirect("admin_tipo_utilizador_list")

    context = {
        "acao": "Editar",
        "tipo": tipo,
    }
    return render(request, "admin/tipos_utilizador/form.html", context)


def admin_tipo_utilizador_delete(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    tipo = get_object_or_404(TipoUtilizador, pk=tipo_id)

    if request.method == "POST":
        nome = tipo.designacao
        tipo.delete()
        messages.success(request, f"Tipo de utilizador '{nome}' removido com sucesso.")
        return redirect("admin_tipo_utilizador_list")

    context = {
        "tipo": tipo,
    }
    return render(request, "admin/tipos_utilizador/confirm_delete.html", context)

# ===============================
#   ADMIN – UTILIZADORES
# ===============================

def admin_user_list(request):
    if not _require_admin_only(request):
        return redirect("home")

    utilizadores = Utilizador.objects.select_related("id_tipo_utilizador").order_by("id_utilizador")

    context = {
        "utilizadores": utilizadores,
    }
    return render(request, "admin/utilizadores/list.html", context)


def admin_user_create(request):
    if not _require_admin_only(request):
        return redirect("home")

    tipos = TipoUtilizador.objects.order_by("designacao")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        morada = request.POST.get("morada", "").strip()
        tipo_id = request.POST.get("tipo_utilizador") or None
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        # validações básicas
        if not nome or not email or not nif or not password:
            messages.error(request, "Preenche nome, email, NIF e password.")
        elif password != password2:
            messages.error(request, "As passwords não coincidem.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        elif Utilizador.objects.filter(email=email).exists():
            messages.error(request, "Já existe um utilizador com esse email.")
        elif Utilizador.objects.filter(nif=nif).exists():
            messages.error(request, "Já existe um utilizador com esse NIF.")
        else:
            tipo_obj = TipoUtilizador.objects.filter(pk=tipo_id).first() if tipo_id else None

            Utilizador.objects.create(
                nome=nome,
                email=email,
                nif=nif,
                morada=morada if morada else None,
                password=make_password(password),
                id_tipo_utilizador=tipo_obj,
            )
            messages.success(request, "Utilizador criado com sucesso.")
            return redirect("admin_user_list")

    context = {
        "tipos": tipos,
        "acao": "Criar",
    }
    return render(request, "admin/utilizadores/form.html", context)


def admin_user_edit(request, user_id):
    if not _require_admin_only(request):
        return redirect("home")

    user = get_object_or_404(Utilizador, pk=user_id)
    tipos = TipoUtilizador.objects.order_by("designacao")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        morada = request.POST.get("morada", "").strip()
        tipo_id = request.POST.get("tipo_utilizador") or None

        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not nome or not email or not nif:
            messages.error(request, "Preenche nome, email e NIF.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        elif Utilizador.objects.filter(email=email).exclude(pk=user_id).exists():
            messages.error(request, "Já existe outro utilizador com esse email.")
        elif Utilizador.objects.filter(nif=nif).exclude(pk=user_id).exists():
            messages.error(request, "Já existe outro utilizador com esse NIF.")
        elif password and password != password2:
            messages.error(request, "As passwords não coincidem.")
        else:
            user.nome = nome
            user.email = email
            user.nif = nif
            user.morada = morada if morada else None
            user.id_tipo_utilizador = (
                TipoUtilizador.objects.filter(pk=tipo_id).first() if tipo_id else None
            )

            if password:
                user.password = make_password(password)

            user.save()
            messages.success(request, "Utilizador atualizado com sucesso.")
            return redirect("admin_user_list")

    context = {
        "acao": "Editar",
        "utilizador": user,
        "tipos": tipos,
    }
    return render(request, "admin/utilizadores/form.html", context)


def admin_user_delete(request, user_id):
    if not _require_admin_only(request):
        return redirect("home")

    user = get_object_or_404(Utilizador, pk=user_id)

    if request.method == "POST":
        nome = user.nome
        user.delete()
        messages.success(request, f"Utilizador '{nome}' removido com sucesso.")
        return redirect("admin_user_list")

    context = {
        "utilizador": user,
    }
    return render(request, "admin/utilizadores/confirm_delete.html", context)

# ===============================
#   ADMIN – PRODUTOS PENDENTES
# ===============================

def admin_product_pending_list(request):
    if not _require_admin(request):
        return redirect("home")

    # Só produtos com aprovação em falta E estado "Pendente"
    produtos = (
        Produto.objects
        .select_related("id_tipo_produto", "id_fornecedor")
        .filter(is_approved=False, estado_produto__iexact="Pendente")
        .order_by("id_produto")
    )

    context = {
        "produtos": produtos,
    }
    return render(request, "admin/produtos/pendentes.html", context)


def admin_product_approve(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == "POST":
        produto.is_approved = True
        # se estiver marcado como Pendente, ao aprovar passa a Ativo
        if produto.estado_produto.lower() == "pendente":
            produto.estado_produto = "Ativo"
        produto.save()

        messages.success(request, f"Produto '{produto.nome}' aprovado com sucesso.")
        return redirect("admin_product_pending_list")

    # se alguém tentar aceder por GET, redirecionamos para pendentes
    return redirect("admin_product_pending_list")

def admin_product_reject(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == "POST":
        produto.is_approved = False  # continua não aprovado
        produto.estado_produto = "Rejeitado"
        produto.save()

        messages.success(request, f"Produto '{produto.nome}' rejeitado com sucesso.")
        return redirect("admin_product_pending_list")

    return redirect("admin_product_pending_list")


# ===============================
#   ADMIN – ENCOMENDAS
# ===============================

def admin_encomenda_list(request):
    if not _require_admin(request):
        return redirect("home")

    encomendas = (
        Encomenda.objects
        .select_related("id_utilizador")
        .order_by("-data_encomenda", "-id_encomenda")
    )

    context = {
        "encomendas": encomendas,
    }
    return render(request, "admin/encomendas/list.html", context)


def admin_encomenda_create(request):
    if not _require_admin(request):
        return redirect("home")

    utilizadores = Utilizador.objects.order_by("nome")

    if request.method == "POST":
        data_str = request.POST.get("data_encomenda", "").strip()
        utilizador_id = request.POST.get("utilizador")
        estado = request.POST.get("estado_encomenda", "").strip() or "Pendente"

        if not data_str or not utilizador_id:
            messages.error(request, "Preenche a data e escolhe um utilizador.")
        else:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Data inválida.")
                data = None

            user = Utilizador.objects.filter(pk=utilizador_id).first()

            if data and user:
                Encomenda.objects.create(
                    data_encomenda=data,
                    id_utilizador=user,
                    estado_encomenda=estado,
                )
                messages.success(request, "Encomenda criada com sucesso.")
                return redirect("admin_encomenda_list")

    context = {
        "acao": "Criar",
        "utilizadores": utilizadores,
    }
    return render(request, "admin/encomendas/form.html", context)


def admin_encomenda_edit(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = get_object_or_404(Encomenda, pk=encomenda_id)
    utilizadores = Utilizador.objects.order_by("nome")

    if request.method == "POST":
        data_str = request.POST.get("data_encomenda", "").strip()
        utilizador_id = request.POST.get("utilizador")
        estado = request.POST.get("estado_encomenda", "").strip() or "Pendente"

        if not data_str or not utilizador_id:
            messages.error(request, "Preenche a data e escolhe um utilizador.")
        else:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Data inválida.")
                data = None

            user = Utilizador.objects.filter(pk=utilizador_id).first()

            if data and user:
                encomenda.data_encomenda = data
                encomenda.id_utilizador = user
                encomenda.estado_encomenda = estado
                encomenda.save()

                messages.success(request, "Encomenda atualizada com sucesso.")
                return redirect("admin_encomenda_list")

    context = {
        "acao": "Editar",
        "encomenda": encomenda,
        "utilizadores": utilizadores,
    }
    return render(request, "admin/encomendas/form.html", context)


def admin_encomenda_delete(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = get_object_or_404(Encomenda, pk=encomenda_id)

    if request.method == "POST":
        num = encomenda.id_encomenda
        encomenda.delete()
        messages.success(request, f"Encomenda #{num} removida com sucesso.")
        return redirect("admin_encomenda_list")

    context = {
        "encomenda": encomenda,
    }
    return render(request, "admin/encomendas/confirm_delete.html", context)

# ===============================
#   ADMIN – ENCOMENDAS · DETALHE
# ===============================

def admin_encomenda_detail(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = get_object_or_404(
        Encomenda.objects.select_related("id_utilizador"),
        pk=encomenda_id
    )

    # Linhas da encomenda
    linhas = (
        EncomendaProduto.objects
        .filter(id_encomenda=encomenda)
        .select_related("id_produto")
        .order_by("id_produto__nome")
    )

    # Produtos disponíveis para adicionar
    produtos = (
        Produto.objects
        .filter(is_approved=True, estado_produto="Ativo")
        .order_by("nome")
    )

    # Cálculo do total da encomenda
    total_encomenda = Decimal("0.00")
    for linha in linhas:
        if linha.id_produto and linha.id_produto.preco is not None:
            total_encomenda += linha.id_produto.preco * linha.quantidade

    context = {
        "encomenda": encomenda,
        "linhas": linhas,
        "produtos": produtos,
        "total_encomenda": total_encomenda,
    }
    return render(request, "admin/encomendas/detail.html", context)


def admin_encomenda_add_item(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = get_object_or_404(Encomenda, pk=encomenda_id)

    if request.method == "POST":
        produto_id = request.POST.get("produto")
        quantidade_str = request.POST.get("quantidade", "1").strip()

        # validações simples
        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "A quantidade deve ser um número inteiro maior que zero.")
            return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

        produto = Produto.objects.filter(pk=produto_id).first()
        if not produto:
            messages.error(request, "Produto inválido.")
            return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

        # criar ou atualizar linha
        linha, created = EncomendaProduto.objects.get_or_create(
            id_encomenda=encomenda,
            id_produto=produto,
            defaults={"quantidade": quantidade},
        )
        if not created:
            linha.quantidade += quantidade
            linha.save()

        messages.success(request, "Produto adicionado/atualizado na encomenda.")
        return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

    return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)


def admin_encomenda_update_item(request, encomenda_id, produto_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = get_object_or_404(Encomenda, pk=encomenda_id)
    linha = get_object_or_404(
        EncomendaProduto,
        id_encomenda=encomenda,
        id_produto_id=produto_id,
    )

    if request.method == "POST":
        quantidade_str = request.POST.get("quantidade", "").strip()

        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "A quantidade deve ser um número inteiro maior que zero.")
            return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

        linha.quantidade = quantidade
        linha.save()
        messages.success(request, "Linha de encomenda atualizada.")
        return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

    return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)


def admin_encomenda_delete_item(request, encomenda_id, produto_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = get_object_or_404(Encomenda, pk=encomenda_id)
    linha = get_object_or_404(
        EncomendaProduto,
        id_encomenda=encomenda,
        id_produto_id=produto_id,
    )

    if request.method == "POST":
        linha.delete()
        messages.success(request, "Linha de encomenda removida.")
        return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

    return redirect("admin_encomenda_detail", encomenda_id=encomenda.id_encomenda)

# ===============================
#   ADMIN – NOTÍCIAS
# ===============================

def admin_noticia_list(request):
    if not _require_admin(request):  # admin + gestor
        return redirect("home")

    noticias = (
        Noticia.objects
        .select_related("id_tipo_noticia", "autor")
        .order_by("-data_publicacao", "-id_noticia")
    )

    context = {
        "noticias": noticias,
    }
    return render(request, "admin/noticias/list.html", context)


def admin_noticia_create(request):
    if not _require_admin(request):
        return redirect("home")

    tipos = TipoNoticia.objects.order_by("nome")
    utilizadores = Utilizador.objects.order_by("nome")

    autor_session_id = request.session.get("user_id")
    autor_selecionado_id = None

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        conteudo = request.POST.get("conteudo", "").strip()
        tipo_id = request.POST.get("tipo_noticia") or None
        autor_id = request.POST.get("autor") or None
        data_str = request.POST.get("data_publicacao", "").strip()

        autor_selecionado_id = int(autor_id) if autor_id else None

        if not titulo or not conteudo or not data_str:
            messages.error(request, "Preenche título, conteúdo e data de publicação.")
        else:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Data de publicação inválida.")
                data = None

            if data:
                tipo_obj = TipoNoticia.objects.filter(pk=tipo_id).first() if tipo_id else None
                autor_obj = Utilizador.objects.filter(pk=autor_id).first() if autor_id else None

                Noticia.objects.create(
                    titulo=titulo,
                    conteudo=conteudo,
                    data_publicacao=data,
                    id_tipo_noticia=tipo_obj,
                    autor=autor_obj,
                )
                messages.success(request, "Notícia criada com sucesso.")
                return redirect("admin_noticia_list")

    # se for GET e ainda não houver seleção, usamos o utilizador em sessão
    if autor_selecionado_id is None and autor_session_id:
        autor_selecionado_id = autor_session_id

    context = {
        "acao": "Criar",
        "tipos": tipos,
        "utilizadores": utilizadores,
        "autor_selecionado_id": autor_selecionado_id,
        "noticia": None,
    }
    return render(request, "admin/noticias/form.html", context)


def admin_noticia_edit(request, noticia_id):
    if not _require_admin(request):
        return redirect("home")

    noticia = get_object_or_404(Noticia, pk=noticia_id)
    tipos = TipoNoticia.objects.order_by("nome")
    utilizadores = Utilizador.objects.order_by("nome")

    autor_selecionado_id = noticia.autor.id_utilizador if noticia.autor else None

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        conteudo = request.POST.get("conteudo", "").strip()
        tipo_id = request.POST.get("tipo_noticia") or None
        autor_id = request.POST.get("autor") or None
        data_str = request.POST.get("data_publicacao", "").strip()

        autor_selecionado_id = int(autor_id) if autor_id else None

        if not titulo or not conteudo or not data_str:
            messages.error(request, "Preenche título, conteúdo e data de publicação.")
        else:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Data de publicação inválida.")
                data = None

            if data:
                noticia.titulo = titulo
                noticia.conteudo = conteudo
                noticia.data_publicacao = data
                noticia.id_tipo_noticia = (
                    TipoNoticia.objects.filter(pk=tipo_id).first() if tipo_id else None
                )
                noticia.autor = (
                    Utilizador.objects.filter(pk=autor_id).first() if autor_id else None
                )
                noticia.save()

                messages.success(request, "Notícia atualizada com sucesso.")
                return redirect("admin_noticia_list")

    context = {
        "acao": "Editar",
        "noticia": noticia,
        "tipos": tipos,
        "utilizadores": utilizadores,
        "autor_selecionado_id": autor_selecionado_id,
    }
    return render(request, "admin/noticias/form.html", context)



def admin_noticia_delete(request, noticia_id):
    if not _require_admin(request):
        return redirect("home")

    noticia = get_object_or_404(Noticia, pk=noticia_id)

    if request.method == "POST":
        titulo = noticia.titulo
        noticia.delete()
        messages.success(request, f"Notícia \"{titulo}\" removida com sucesso.")
        return redirect("admin_noticia_list")

    context = {
        "noticia": noticia,
    }
    return render(request, "admin/noticias/confirm_delete.html", context)


def minhas_encomendas(request):
    # Tem de estar autenticado
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para veres as tuas encomendas.")
        return redirect("login")

    user = get_object_or_404(Utilizador, pk=user_id)

    # Buscar encomendas do utilizador + linhas com produtos
    encomendas = (
        Encomenda.objects
        .filter(id_utilizador=user)
        .prefetch_related("linhas__id_produto")
        .order_by("-data_encomenda", "-id_encomenda")
    )

    # Calcular total de cada encomenda
    encomendas_info = []
    for enc in encomendas:
        total = Decimal("0.00")
        for linha in enc.linhas.all():
            if linha.id_produto and linha.id_produto.preco is not None:
                total += linha.id_produto.preco * linha.quantidade
        encomendas_info.append({
            "encomenda": enc,
            "total": total,
        })

    context = {
        "user": user,
        "encomendas_info": encomendas_info,
    }
    return render(request, "conta/minhas_encomendas.html", context)

def minha_encomenda_detail(request, encomenda_id):
    # Utilizador tem de estar autenticado
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para veres as tuas encomendas.")
        return redirect("login")

    user = get_object_or_404(Utilizador, pk=user_id)

    # Garantir que a encomenda pertence a este utilizador
    encomenda = get_object_or_404(
        Encomenda.objects.prefetch_related("linhas__id_produto"),
        pk=encomenda_id,
        id_utilizador=user,
    )

    # Calcular total
    total = Decimal("0.00")
    for linha in encomenda.linhas.all():
        if linha.id_produto and linha.id_produto.preco is not None:
            total += linha.id_produto.preco * linha.quantidade

    context = {
        "user": user,
        "encomenda": encomenda,
        "linhas": encomenda.linhas.all(),
        "total_encomenda": total,
    }
    return render(request, "conta/encomenda_detalhe.html", context)

# ===============================
#   LOJA / CLIENTE – PRODUTOS E CARRINHO
# ===============================

def loja_produtos(request):
    # só mostra produtos aprovados e ativos
    produtos = (
        Produto.objects
        .filter(is_approved=True, estado_produto="Ativo")
        .order_by("nome")
    )
    context = {"produtos": produtos}
    return render(request, "loja/produtos.html", context)


def _require_login_for_loja(request):
    """Devolve o Utilizador logado ou None se não estiver autenticado."""
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para usar o carrinho.")
        return None
    return get_object_or_404(Utilizador, pk=user_id)


def loja_adicionar_produto(request, produto_id):
    if request.method != "POST":
        return redirect("loja_produtos")

    user = _require_login_for_loja(request)
    if user is None:
        return redirect("login")

    produto = get_object_or_404(
        Produto,
        pk=produto_id,
        is_approved=True,
        estado_produto="Ativo",
    )

    qtd_str = request.POST.get("quantidade", "1").strip()
    try:
        quantidade = int(qtd_str)
        if quantidade <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect("loja_produtos")

    # encontrar ou criar a encomenda em estado "Carrinho"
    encomenda, _ = Encomenda.objects.get_or_create(
        id_utilizador=user,
        estado_encomenda="Carrinho",
        defaults={"data_encomenda": date.today()},
    )

    # ver se já existe uma linha para este produto
    linha = EncomendaProduto.objects.filter(
        id_encomenda=encomenda,
        id_produto=produto,
    ).first()

    if linha:
        linha.quantidade += quantidade
        linha.save()
    else:
        EncomendaProduto.objects.create(
            id_encomenda=encomenda,
            id_produto=produto,
            quantidade=quantidade,
        )

    messages.success(request, "Produto adicionado ao carrinho.")
    return redirect("loja_carrinho")


def loja_carrinho(request):
    user = _require_login_for_loja(request)
    if user is None:
        return redirect("login")

    carrinho = (
        Encomenda.objects
        .filter(id_utilizador=user, estado_encomenda="Carrinho")
        .prefetch_related("linhas__id_produto")
        .first()
    )

    linhas = list(carrinho.linhas.all()) if carrinho else []
    total = Decimal("0.00")
    for linha in linhas:
        if linha.id_produto and linha.id_produto.preco is not None:
            total += linha.id_produto.preco * linha.quantidade

    context = {
        "carrinho": carrinho,
        "linhas": linhas,
        "total_encomenda": total,
    }
    return render(request, "loja/carrinho.html", context)


def loja_remover_linha(request, linha_id):
    user = _require_login_for_loja(request)
    if user is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    # garantir que a linha pertence a uma encomenda "Carrinho" deste utilizador
    linha = get_object_or_404(
        EncomendaProduto.objects.select_related("id_encomenda__id_utilizador"),
        pk=linha_id,
    )
    if (
        linha.id_encomenda.id_utilizador_id != user.id_utilizador
        or linha.id_encomenda.estado_encomenda != "Carrinho"
    ):
        messages.error(request, "Não podes alterar este carrinho.")
        return redirect("loja_carrinho")

    linha.delete()
    messages.success(request, "Produto removido do carrinho.")
    return redirect("loja_carrinho")


def loja_finalizar_encomenda(request):
    user = _require_login_for_loja(request)
    if user is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    carrinho = (
        Encomenda.objects
        .filter(id_utilizador=user, estado_encomenda="Carrinho")
        .prefetch_related("linhas")
        .first()
    )

    if not carrinho or not carrinho.linhas.exists():
        messages.error(request, "O teu carrinho está vazio.")
        return redirect("loja_carrinho")

    carrinho.estado_encomenda = "Pendente"   # passa de Carrinho -> Pendente
    carrinho.data_encomenda = date.today()
    carrinho.save()

    messages.success(
        request,
        "Encomenda criada com sucesso! Podes acompanhar o estado em 'As minhas encomendas'."
    )
    return redirect("minhas_encomendas")

# ===============================
#   CLIENTE – NOTÍCIAS (READ ONLY)
# ===============================

def noticias_lista(request):
    noticias = (
        Noticia.objects
        .select_related("id_tipo_noticia", "autor")
        .order_by("-data_publicacao", "-id_noticia")
    )
    context = {"noticias": noticias}
    return render(request, "noticias/lista.html", context)


def noticia_detalhe(request, noticia_id):
    noticia = get_object_or_404(
        Noticia.objects.select_related("id_tipo_noticia", "autor"),
        pk=noticia_id,
    )
    context = {"noticia": noticia}
    return render(request, "noticias/detalhe.html", context)
