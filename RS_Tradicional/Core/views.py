# Core/views.py
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

from django.db import connection, DatabaseError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

# ======================================================
#  HELPERS GENÉRICOS PARA SQL
# ======================================================

def _fetchall_dicts(sql, params=None):
    """
    Executa um SELECT e devolve lista de dicts:
    [{"col1": valor, "col2": valor, ...}, ...]
    """
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def _fetchone_dict(sql, params=None):
    """
    Executa um SELECT que devolve 0 ou 1 linha.
    Retorna um dict ou None.
    """
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        cols = [c[0] for c in cur.description]
        row = cur.fetchone()
    if not row:
        return None
    return dict(zip(cols, row))


def _user_friendly_db_error(err: str) -> str:
    if not err:
        return "Ocorreu um erro. Tenta novamente."

    # remover lixo do postgres
    cleaned = err.split("CONTEXT:")[0].strip()
    cleaned = cleaned.replace("\n", " ").strip()

    # mapear mensagens conhecidas para UI
    msg = cleaned.lower()

    if "apenas clientes podem usar o carrinho" in msg:
        return "Apenas clientes podem usar o carrinho."
    if "produto inválido ou inativo" in msg:
        return "Este produto não está disponível."
    if "stock insuficiente" in msg or "excede o stock" in msg:
        return "Não existe stock suficiente para essa quantidade."
    if "não existe carrinho" in msg:
        return "O teu carrinho está vazio."
    if "quantidade inválida" in msg:
        return "Quantidade inválida."

    # fallback curto (sem contexto)
    return cleaned


def _safe_callproc(proc_name, params=None):
    """
    Chama uma stored procedure com tratamento de erro.
    Devolve (ok: bool, erro: str|None).
    """
    params = params or []
    placeholders = ", ".join(["%s"] * len(params))

    try:
        with connection.cursor() as cur:
            cur.execute(f"CALL {proc_name}({placeholders})", params)
        return True, None
    except DatabaseError as e:
        return False, str(e.__cause__ or e)


# ======================================================
#  HELPERS DE PERMISSÕES
# ======================================================

def _require_cliente(request):
    user_id = request.session.get("user_id")
    user_tipo = (request.session.get("user_tipo") or "").lower()

    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para usar o carrinho.")
        return None

    if user_tipo != "cliente":
        messages.error(request, "Apenas clientes podem usar o carrinho.")
        return None

    return user_id


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


def _require_login_for_loja(request):
    """
    Devolve o id do utilizador logado ou None se não estiver autenticado.
    (Usado na loja/carrinho.)
    """
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para usar o carrinho.")
        return None
    return user_id


# ======================================================
#  HOME / ADMIN DASHBOARD
# ======================================================

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


# ======================================================
#  ADMIN – PRODUTOS
# ======================================================

def admin_product_list(request):
    if not _require_admin(request):
        return redirect("home")

    produtos = _fetchall_dicts("""
        SELECT
            id_produto,
            nome,
            descricao,
            preco,
            stock,
            is_approved,
            estado_produto,
            id_tipo_produto,
            tipo_designacao,
            id_fornecedor,
            fornecedor_nome
        FROM vw_admin_produtos
        ORDER BY id_produto
    """)

    context = {"produtos": produtos}
    return render(request, "admin/produtos/list.html", context)


def admin_product_create(request):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_produto, designacao
        FROM vw_tipos_produto
        ORDER BY designacao
    """)
    fornecedores = _fetchall_dicts("""
        SELECT id_fornecedor, nome
        FROM vw_fornecedores
        ORDER BY nome
    """)

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
                ok, erro = _safe_callproc(
                    "sp_admin_produto_criar",
                    [
                        exec_id,
                        nome,
                        descricao or None,
                        preco,
                        stock,
                        estado,
                        is_approved,
                        int(tipo_id) if tipo_id else None,
                        int(fornecedor_id) if fornecedor_id else None,
                    ],
                )
                if not ok:
                    messages.error(request, f"Erro ao criar produto: {erro}")
                else:
                    messages.success(request, "Produto criado com sucesso.")
                    return redirect("admin_product_list")

    context = {
        "tipos": tipos,
        "fornecedores": fornecedores,
        "acao": "Criar",
        "produto": None,
    }
    return render(request, "admin/produtos/form.html", context)


def admin_product_edit(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    produto = _fetchone_dict("""
        SELECT
            id_produto,
            nome,
            descricao,
            preco,
            stock,
            is_approved,
            estado_produto,
            id_tipo_produto,
            tipo_designacao,
            id_fornecedor,
            fornecedor_nome
        FROM vw_admin_produtos
        WHERE id_produto = %s
    """, [produto_id])

    if not produto:
        messages.error(request, "Produto não encontrado.")
        return redirect("admin_product_list")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_produto, designacao
        FROM vw_tipos_produto
        ORDER BY designacao
    """)

    fornecedores = _fetchall_dicts("""
        SELECT id_fornecedor, nome
        FROM vw_fornecedores
        ORDER BY nome
    """)

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
                ok, erro = _safe_callproc(
                    "sp_admin_produto_atualizar",
                    [
                        exec_id,
                        produto_id,
                        nome,
                        descricao or None,
                        preco,
                        stock,
                        estado,
                        is_approved,
                        int(tipo_id) if tipo_id else None,
                        int(fornecedor_id) if fornecedor_id else None,
                    ],
                )
                if not ok:
                    messages.error(request, f"Erro ao atualizar produto: {erro}")
                else:
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

    exec_id = request.session.get("user_id")

    produto = _fetchone_dict("""
        SELECT id_produto, nome
        FROM vw_admin_produtos
        WHERE id_produto = %s
    """, [produto_id])

    if not produto:
        messages.error(request, "Produto não encontrado.")
        return redirect("admin_product_list")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_produto_apagar", [exec_id, produto_id])
        if not ok:
            messages.error(request, f"Erro ao remover produto: {erro}")
        else:
            messages.success(request, f"Produto '{produto['nome']}' removido com sucesso.")
        return redirect("admin_product_list")

    context = {"produto": produto}
    return render(request, "admin/produtos/confirm_delete.html", context)


def admin_product_pending_list(request):
    if not _require_admin(request):
        return redirect("home")

    produtos = _fetchall_dicts("""
        SELECT
            id_produto,
            nome,
            descricao,
            preco,
            stock,
            is_approved,
            estado_produto,
            tipo_designacao,
            fornecedor_nome
        FROM vw_admin_produtos
        WHERE is_approved = FALSE
          AND LOWER(estado_produto) = 'pendente'
        ORDER BY id_produto
    """)

    context = {"produtos": produtos}
    return render(request, "admin/produtos/pendentes.html", context)


def admin_product_approve(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_aprovar_produto", [exec_id, produto_id])
        if not ok:
            messages.error(request, f"Erro ao aprovar produto: {erro}")
        else:
            messages.success(request, "Produto aprovado com sucesso.")
    return redirect("admin_product_pending_list")


def admin_product_reject(request, produto_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_rejeitar_produto", [exec_id, produto_id])
        if not ok:
            messages.error(request, f"Erro ao rejeitar produto: {erro}")
        else:
            messages.success(request, "Produto rejeitado com sucesso.")
    return redirect("admin_product_pending_list")


# ======================================================
#  ADMIN – TIPOS DE PRODUTO
# ======================================================

def admin_tipo_produto_list(request):
    if not _require_admin(request):
        return redirect("home")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_produto, designacao
        FROM vw_tipos_produto
        ORDER BY designacao
    """)

    context = {"tipos": tipos}
    return render(request, "admin/tipos_produto/list.html", context)


def admin_tipo_produto_create(request):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            ok, erro = _safe_callproc("sp_admin_tipo_produto_criar", [exec_id, designacao])
            if not ok:
                messages.error(request, f"Erro ao criar tipo de produto: {erro}")
            else:
                messages.success(request, "Tipo de produto criado com sucesso.")
                return redirect("admin_tipo_produto_list")

    context = {"acao": "Criar"}
    return render(request, "admin/tipos_produto/form.html", context)


def admin_tipo_produto_edit(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    tipo = _fetchone_dict("""
        SELECT id_tipo_produto, designacao
        FROM vw_tipos_produto
        WHERE id_tipo_produto = %s
    """, [tipo_id])

    if not tipo:
        messages.error(request, "Tipo de produto não encontrado.")
        return redirect("admin_tipo_produto_list")

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            ok, erro = _safe_callproc("sp_admin_tipo_produto_atualizar", [exec_id, tipo_id, designacao])
            if not ok:
                messages.error(request, f"Erro ao atualizar tipo de produto: {erro}")
            else:
                messages.success(request, "Tipo de produto atualizado com sucesso.")
                return redirect("admin_tipo_produto_list")

    context = {"acao": "Editar", "tipo": tipo}
    return render(request, "admin/tipos_produto/form.html", context)


def admin_tipo_produto_delete(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    tipo = _fetchone_dict("""
        SELECT id_tipo_produto, designacao
        FROM vw_tipos_produto
        WHERE id_tipo_produto = %s
    """, [tipo_id])

    if not tipo:
        messages.error(request, "Tipo de produto não encontrado.")
        return redirect("admin_tipo_produto_list")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_tipo_produto_apagar", [exec_id, tipo_id])
        if not ok:
            messages.error(request, f"Erro ao remover tipo de produto: {erro}")
        else:
            messages.success(request, f"Tipo de produto '{tipo['designacao']}' removido com sucesso.")
        return redirect("admin_tipo_produto_list")

    context = {"tipo": tipo}
    return render(request, "admin/tipos_produto/confirm_delete.html", context)


# ======================================================
#  ADMIN – FORNECEDORES
# ======================================================

def admin_fornecedor_list(request):
    if not _require_admin(request):
        return redirect("home")

    fornecedores = _fetchall_dicts("""
        SELECT
            id_fornecedor,
            nome,
            contacto,
            email,
            nif,
            isSingular AS is_singular,
            morada,
            imagem_fornecedor
        FROM vw_fornecedores
        ORDER BY nome
    """)

    context = {"fornecedores": fornecedores}
    return render(request, "admin/fornecedores/list.html", context)


def admin_fornecedor_create(request):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        contacto = request.POST.get("contacto", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        is_singular_str = request.POST.get("is_singular", "on")
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
            ok, erro = _safe_callproc(
                "sp_admin_fornecedor_criar",
                [exec_id, nome, contacto, email, nif, is_singular, morada if morada else None, imagem if imagem else None],
            )
            if not ok:
                messages.error(request, f"Erro ao criar fornecedor: {erro}")
            else:
                messages.success(request, "Fornecedor criado com sucesso.")
                return redirect("admin_fornecedor_list")

    context = {"acao": "Criar"}
    return render(request, "admin/fornecedores/form.html", context)


def admin_fornecedor_edit(request, fornecedor_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    fornecedor = _fetchone_dict("""
        SELECT
            id_fornecedor,
            nome,
            contacto,
            email,
            nif,
            isSingular AS is_singular,
            morada,
            imagem_fornecedor
        FROM vw_fornecedores
        WHERE id_fornecedor = %s
    """, [fornecedor_id])

    if not fornecedor:
        messages.error(request, "Fornecedor não encontrado.")
        return redirect("admin_fornecedor_list")

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
            ok, erro = _safe_callproc(
                "sp_admin_fornecedor_atualizar",
                [exec_id, fornecedor_id, nome, contacto, email, nif, is_singular, morada if morada else None, imagem if imagem else None],
            )
            if not ok:
                messages.error(request, f"Erro ao atualizar fornecedor: {erro}")
            else:
                messages.success(request, "Fornecedor atualizado com sucesso.")
                return redirect("admin_fornecedor_list")

    context = {"acao": "Editar", "fornecedor": fornecedor}
    return render(request, "admin/fornecedores/form.html", context)


def admin_fornecedor_delete(request, fornecedor_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    fornecedor = _fetchone_dict("""
        SELECT id_fornecedor, nome
        FROM vw_fornecedores
        WHERE id_fornecedor = %s
    """, [fornecedor_id])

    if not fornecedor:
        messages.error(request, "Fornecedor não encontrado.")
        return redirect("admin_fornecedor_list")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_fornecedor_apagar", [exec_id, fornecedor_id])
        if not ok:
            messages.error(request, f"Erro ao remover fornecedor: {erro}")
        else:
            messages.success(request, f"Fornecedor '{fornecedor['nome']}' removido com sucesso.")
        return redirect("admin_fornecedor_list")

    context = {"fornecedor": fornecedor}
    return render(request, "admin/fornecedores/confirm_delete.html", context)


# ======================================================
#  FORNECEDOR – SUBMETER PRODUTO / OS MEUS PRODUTOS
# ======================================================

def fornecedor_product_create(request):
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if user_tipo != "fornecedor":
        messages.error(request, "Apenas utilizadores do tipo Fornecedor podem submeter produtos.")
        return redirect("home")

    exec_id = request.session.get("user_id")
    user_email = request.session.get("user_email")

    fornecedor = _fetchone_dict("""
        SELECT id_fornecedor, nome, email
        FROM vw_fornecedores
        WHERE LOWER(email) = LOWER(%s)
    """, [user_email])

    if not fornecedor:
        messages.error(
            request,
            "Não foi encontrado nenhum fornecedor associado ao teu email. "
            "Contacta um administrador."
        )
        return redirect("home")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_produto, designacao
        FROM vw_tipos_produto
        ORDER BY designacao
    """)

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        preco_str = request.POST.get("preco", "").replace(",", ".").strip()
        stock_str = request.POST.get("stock", "").strip()
        tipo_id = request.POST.get("tipo_produto") or None

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
                ok, erro = _safe_callproc(
                    "sp_fornecedor_submeter_produto",
                    [
                        exec_id,
                        nome,
                        descricao or None,
                        preco,
                        stock,
                        int(tipo_id) if tipo_id else None,
                    ],
                )
                if not ok:
                    messages.error(request, f"Erro ao submeter produto: {erro}")
                else:
                    messages.success(
                        request,
                        "Produto submetido com sucesso. Aguarda aprovação de um administrador/gestor."
                    )
                    return redirect("fornecedor_product_list")

    context = {"tipos": tipos, "fornecedor": fornecedor}
    return render(request, "fornecedor/produtos/form.html", context)


def fornecedor_product_list(request):
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if user_tipo != "fornecedor":
        messages.error(request, "Apenas utilizadores do tipo Fornecedor podem aceder a esta área.")
        return redirect("home")

    user_email = request.session.get("user_email")

    fornecedor = _fetchone_dict("""
        SELECT id_fornecedor, nome, email
        FROM vw_fornecedores
        WHERE LOWER(email) = LOWER(%s)
    """, [user_email])

    if not fornecedor:
        messages.error(
            request,
            "Não foi encontrado nenhum fornecedor associado ao teu email. "
            "Contacta um administrador."
        )
        return redirect("home")

    produtos = _fetchall_dicts("""
        SELECT
            id_produto,
            nome,
            descricao,
            preco,
            stock,
            is_approved,
            estado_produto,
            tipo_designacao
        FROM vw_fornecedor_produtos
        WHERE id_fornecedor = %s
        ORDER BY id_produto
    """, [fornecedor["id_fornecedor"]])

    context = {"fornecedor": fornecedor, "produtos": produtos}
    return render(request, "fornecedor/produtos/list.html", context)


# ======================================================
#  ADMIN – TIPOS DE UTILIZADOR
# ======================================================

def admin_tipo_utilizador_list(request):
    if not _require_admin(request):
        return redirect("home")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_utilizador, designacao
        FROM vw_tipos_utilizador
        ORDER BY designacao
    """)

    context = {"tipos": tipos}
    return render(request, "admin/tipos_utilizador/list.html", context)


def admin_tipo_utilizador_create(request):
    if not _require_admin(request):
        return redirect("home")

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            user_id = request.session.get("user_id")

            ok, erro = _safe_callproc("sp_tipo_utilizador_criar", [user_id, designacao])
            if not ok:
                messages.error(request, f"Erro ao criar tipo de utilizador: {erro}")
            else:
                messages.success(request, "Tipo de utilizador criado com sucesso.")
                return redirect("admin_tipo_utilizador_list")

    context = {"acao": "Criar"}
    return render(request, "admin/tipos_utilizador/form.html", context)


def admin_tipo_utilizador_edit(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    tipo = _fetchone_dict("""
        SELECT id_tipo_utilizador, designacao
        FROM vw_tipos_utilizador
        WHERE id_tipo_utilizador = %s
    """, [tipo_id])

    if not tipo:
        messages.error(request, "Tipo de utilizador não encontrado.")
        return redirect("admin_tipo_utilizador_list")

    if request.method == "POST":
        designacao = request.POST.get("designacao", "").strip()

        if not designacao:
            messages.error(request, "A designação é obrigatória.")
        else:
            user_id = request.session.get("user_id")

            ok, erro = _safe_callproc("sp_tipo_utilizador_atualizar", [user_id, tipo_id, designacao])
            if not ok:
                messages.error(request, f"Erro ao atualizar tipo de utilizador: {erro}")
            else:
                messages.success(request, "Tipo de utilizador atualizado com sucesso.")
                return redirect("admin_tipo_utilizador_list")

    context = {"acao": "Editar", "tipo": tipo}
    return render(request, "admin/tipos_utilizador/form.html", context)


def admin_tipo_utilizador_delete(request, tipo_id):
    if not _require_admin(request):
        return redirect("home")

    tipo = _fetchone_dict("""
        SELECT id_tipo_utilizador, designacao
        FROM vw_tipos_utilizador
        WHERE id_tipo_utilizador = %s
    """, [tipo_id])

    if not tipo:
        messages.error(request, "Tipo de utilizador não encontrado.")
        return redirect("admin_tipo_utilizador_list")

    if request.method == "POST":
        user_id = request.session.get("user_id")

        ok, erro = _safe_callproc("sp_tipo_utilizador_apagar", [user_id, tipo_id])
        if not ok:
            messages.error(request, f"Erro ao remover tipo de utilizador: {erro}")
        else:
            messages.success(request, f"Tipo de utilizador '{tipo['designacao']}' removido com sucesso.")
        return redirect("admin_tipo_utilizador_list")

    context = {"tipo": tipo}
    return render(request, "admin/tipos_utilizador/confirm_delete.html", context)


# ======================================================
#  ADMIN – UTILIZADORES (CRUD)
# ======================================================

def admin_user_list(request):
    if not _require_admin_only(request):
        return redirect("home")

    utilizadores = _fetchall_dicts("""
        SELECT
            id_utilizador,
            nome,
            email,
            nif,
            morada,
            id_tipo_utilizador,
            tipo_designacao
        FROM vw_admin_utilizadores
        ORDER BY id_utilizador
    """)

    context = {"utilizadores": utilizadores}
    return render(request, "admin/utilizadores/list.html", context)


def admin_user_create(request):
    if not _require_admin_only(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_utilizador, designacao
        FROM vw_tipos_utilizador
        ORDER BY designacao
    """)

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        morada = request.POST.get("morada", "").strip()
        tipo_id = request.POST.get("tipo_utilizador") or None
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not nome or not email or not nif or not password:
            messages.error(request, "Preenche nome, email, NIF e password.")
        elif password != password2:
            messages.error(request, "As passwords não coincidem.")
        elif len(nif) != 9 or not nif.isdigit():
            messages.error(request, "O NIF deve ter exatamente 9 dígitos.")
        else:
            password_hash = make_password(password)

            ok, erro = _safe_callproc(
                "sp_admin_utilizador_criar",
                [exec_id, nome, email, password_hash, morada if morada else None, nif, int(tipo_id) if tipo_id else None],
            )
            if not ok:
                messages.error(request, f"Erro ao criar utilizador: {erro}")
            else:
                messages.success(request, "Utilizador criado com sucesso.")
                return redirect("admin_user_list")

    context = {"tipos": tipos, "acao": "Criar", "utilizador": None}
    return render(request, "admin/utilizadores/form.html", context)


def admin_user_edit(request, user_id):
    if not _require_admin_only(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    user = _fetchone_dict("""
        SELECT
            id_utilizador,
            nome,
            email,
            morada,
            nif,
            id_tipo_utilizador,
            tipo_designacao
        FROM vw_admin_utilizadores
        WHERE id_utilizador = %s
    """, [user_id])

    if not user:
        messages.error(request, "Utilizador não encontrado.")
        return redirect("admin_user_list")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_utilizador, designacao
        FROM vw_tipos_utilizador
        ORDER BY designacao
    """)

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
        elif password and password != password2:
            messages.error(request, "As passwords não coincidem.")
        else:
            password_hash = make_password(password) if password else None

            ok, erro = _safe_callproc(
                "sp_admin_utilizador_atualizar",
                [exec_id, user_id, nome, email, password_hash, morada if morada else None, nif, int(tipo_id) if tipo_id else None],
            )
            if not ok:
                messages.error(request, f"Erro ao atualizar utilizador: {erro}")
            else:
                messages.success(request, "Utilizador atualizado com sucesso.")
                return redirect("admin_user_list")

    context = {"acao": "Editar", "utilizador": user, "tipos": tipos}
    return render(request, "admin/utilizadores/form.html", context)


def admin_user_delete(request, user_id):
    if not _require_admin_only(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    user = _fetchone_dict("""
        SELECT id_utilizador, nome
        FROM vw_admin_utilizadores
        WHERE id_utilizador = %s
    """, [user_id])

    if not user:
        messages.error(request, "Utilizador não encontrado.")
        return redirect("admin_user_list")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_utilizador_apagar", [exec_id, user_id])
        if not ok:
            messages.error(request, f"Erro ao remover utilizador: {erro}")
        else:
            messages.success(request, f"Utilizador '{user['nome']}' removido com sucesso.")
        return redirect("admin_user_list")

    context = {"utilizador": user}
    return render(request, "admin/utilizadores/confirm_delete.html", context)


# ======================================================
#  ADMIN – ENCOMENDAS
# ======================================================

def admin_encomenda_list(request):
    if not _require_admin(request):
        return redirect("home")

    encomendas = _fetchall_dicts("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda,
            id_utilizador,
            utilizador_nome,
            utilizador_email
        FROM vw_admin_encomendas
        ORDER BY data_encomenda DESC, id_encomenda DESC
    """)

    context = {"encomendas": encomendas}
    return render(request, "admin/encomendas/list.html", context)


def admin_encomenda_create(request):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    utilizadores = _fetchall_dicts("""
        SELECT id_utilizador, nome
        FROM vw_admin_utilizadores
        ORDER BY nome
    """)

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

            if data:
                ok, erro = _safe_callproc("sp_admin_encomenda_criar", [exec_id, data, int(utilizador_id), estado])
                if not ok:
                    messages.error(request, f"Erro ao criar encomenda: {erro}")
                else:
                    messages.success(request, "Encomenda criada com sucesso.")
                    return redirect("admin_encomenda_list")

    context = {"acao": "Criar", "utilizadores": utilizadores, "encomenda": None}
    return render(request, "admin/encomendas/form.html", context)


def admin_encomenda_edit(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    encomenda = _fetchone_dict("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda,
            id_utilizador,
            utilizador_nome
        FROM vw_admin_encomendas
        WHERE id_encomenda = %s
    """, [encomenda_id])

    if not encomenda:
        messages.error(request, "Encomenda não encontrada.")
        return redirect("admin_encomenda_list")

    utilizadores = _fetchall_dicts("""
        SELECT id_utilizador, nome
        FROM vw_admin_utilizadores
        ORDER BY nome
    """)

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

            if data:
                ok, erro = _safe_callproc("sp_admin_encomenda_atualizar", [exec_id, encomenda_id, data, int(utilizador_id), estado])
                if not ok:
                    messages.error(request, f"Erro ao atualizar encomenda: {erro}")
                else:
                    messages.success(request, "Encomenda atualizada com sucesso.")
                    return redirect("admin_encomenda_list")

    context = {"acao": "Editar", "encomenda": encomenda, "utilizadores": utilizadores}
    return render(request, "admin/encomendas/form.html", context)


def admin_encomenda_delete(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    encomenda = _fetchone_dict("""
        SELECT id_encomenda
        FROM vw_admin_encomendas
        WHERE id_encomenda = %s
    """, [encomenda_id])

    if not encomenda:
        messages.error(request, "Encomenda não encontrada.")
        return redirect("admin_encomenda_list")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_encomenda_apagar", [exec_id, encomenda_id])
        if not ok:
            messages.error(request, f"Erro ao remover encomenda: {erro}")
        else:
            messages.success(request, f"Encomenda #{encomenda_id} removida com sucesso.")
        return redirect("admin_encomenda_list")

    context = {"encomenda": encomenda}
    return render(request, "admin/encomendas/confirm_delete.html", context)


def admin_encomenda_detail(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    encomenda = _fetchone_dict("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda,
            id_utilizador,
            utilizador_nome
        FROM vw_admin_encomendas
        WHERE id_encomenda = %s
    """, [encomenda_id])

    if not encomenda:
        messages.error(request, "Encomenda não encontrada.")
        return redirect("admin_encomenda_list")

    linhas = _fetchall_dicts("""
        SELECT
            id_encomenda,
            id_produto,
            nome_produto,
            preco_produto,
            quantidade
        FROM vw_admin_encomenda_linhas
        WHERE id_encomenda = %s
        ORDER BY nome_produto
    """, [encomenda_id])

    total_encomenda = Decimal("0.00")
    for linha in linhas:
        if linha["preco_produto"] is not None:
            total_encomenda += linha["preco_produto"] * linha["quantidade"]

    produtos = _fetchall_dicts("""
        SELECT id_produto, nome
        FROM vw_loja_produtos
        ORDER BY nome
    """)

    context = {"encomenda": encomenda, "linhas": linhas, "produtos": produtos, "total_encomenda": total_encomenda}
    return render(request, "admin/encomendas/detail.html", context)


def admin_encomenda_add_item(request, encomenda_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        produto_id = request.POST.get("produto")
        quantidade_str = request.POST.get("quantidade", "1").strip()

        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "A quantidade deve ser um número inteiro maior que zero.")
            return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)

        ok, erro = _safe_callproc("sp_admin_encomenda_adicionar_linha", [exec_id, encomenda_id, int(produto_id), quantidade])
        if not ok:
            messages.error(request, f"Erro ao adicionar produto à encomenda: {erro}")
        else:
            messages.success(request, "Produto adicionado/atualizado na encomenda.")
        return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)

    return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)


def admin_encomenda_update_item(request, encomenda_id, produto_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        quantidade_str = request.POST.get("quantidade", "").strip()

        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "A quantidade deve ser um número inteiro maior que zero.")
            return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)

        ok, erro = _safe_callproc("sp_admin_encomenda_atualizar_linha", [exec_id, encomenda_id, produto_id, quantidade])
        if not ok:
            messages.error(request, f"Erro ao atualizar linha de encomenda: {erro}")
        else:
            messages.success(request, "Linha de encomenda atualizada.")
        return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)

    return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)


def admin_encomenda_delete_item(request, encomenda_id, produto_id):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_encomenda_remover_linha", [exec_id, encomenda_id, produto_id])
        if not ok:
            messages.error(request, f"Erro ao remover linha de encomenda: {erro}")
        else:
            messages.success(request, "Linha de encomenda removida.")
        return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)

    return redirect("admin_encomenda_detail", encomenda_id=encomenda_id)


# ======================================================
#  ADMIN / CLIENTE – NOTÍCIAS
# ======================================================

def admin_noticia_list(request):
    if not _require_admin(request):
        return redirect("home")

    noticias = _fetchall_dicts("""
        SELECT
            id_noticia,
            titulo,
            conteudo,
            data_publicacao,
            tipo_noticia,
            id_tipo_noticia,
            autor_nome,
            autor_id
        FROM vw_admin_noticias
        ORDER BY data_publicacao DESC, id_noticia DESC
    """)

    context = {"noticias": noticias}
    return render(request, "admin/noticias/list.html", context)


def admin_noticia_create(request):
    if not _require_admin(request):
        return redirect("home")

    exec_id = request.session.get("user_id")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_noticia, nome
        FROM vw_tipos_noticia
        ORDER BY nome
    """)

    utilizadores = _fetchall_dicts("""
        SELECT id_utilizador, nome
        FROM vw_admin_utilizadores
        ORDER BY nome
    """)

    autor_session_id = request.session.get("user_id")
    autor_selecionado_id = autor_session_id

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
                data_pub = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Data de publicação inválida.")
                data_pub = None

            if data_pub:
                ok, erro = _safe_callproc(
                    "sp_admin_noticia_criar",
                    [exec_id, titulo, conteudo, data_pub, int(tipo_id) if tipo_id else None, int(autor_id) if autor_id else None],
                )
                if not ok:
                    messages.error(request, f"Erro ao criar notícia: {erro}")
                else:
                    messages.success(request, "Notícia criada com sucesso.")
                    return redirect("admin_noticia_list")

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

    exec_id = request.session.get("user_id")

    noticia = _fetchone_dict("""
        SELECT
            id_noticia,
            titulo,
            conteudo,
            data_publicacao,
            id_tipo_noticia,
            tipo_noticia,
            autor_id,
            autor_nome
        FROM vw_admin_noticias
        WHERE id_noticia = %s
    """, [noticia_id])

    if not noticia:
        messages.error(request, "Notícia não encontrada.")
        return redirect("admin_noticia_list")

    tipos = _fetchall_dicts("""
        SELECT id_tipo_noticia, nome
        FROM vw_tipos_noticia
        ORDER BY nome
    """)

    utilizadores = _fetchall_dicts("""
        SELECT id_utilizador, nome
        FROM vw_admin_utilizadores
        ORDER BY nome
    """)

    autor_selecionado_id = noticia.get("autor_id")

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
                data_pub = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Data de publicação inválida.")
                data_pub = None

            if data_pub:
                ok, erro = _safe_callproc(
                    "sp_admin_noticia_atualizar",
                    [exec_id, noticia_id, titulo, conteudo, data_pub, int(tipo_id) if tipo_id else None, int(autor_id) if autor_id else None],
                )
                if not ok:
                    messages.error(request, f"Erro ao atualizar notícia: {erro}")
                else:
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

    exec_id = request.session.get("user_id")

    noticia = _fetchone_dict("""
        SELECT id_noticia, titulo
        FROM vw_admin_noticias
        WHERE id_noticia = %s
    """, [noticia_id])

    if not noticia:
        messages.error(request, "Notícia não encontrada.")
        return redirect("admin_noticia_list")

    if request.method == "POST":
        ok, erro = _safe_callproc("sp_admin_noticia_apagar", [exec_id, noticia_id])
        if not ok:
            messages.error(request, f"Erro ao remover notícia: {erro}")
        else:
            messages.success(request, f"Notícia \"{noticia['titulo']}\" removida com sucesso.")
        return redirect("admin_noticia_list")

    context = {"noticia": noticia}
    return render(request, "admin/noticias/confirm_delete.html", context)


def noticias_lista(request):
    noticias = _fetchall_dicts("""
    SELECT
        id_noticia,
        titulo,
        conteudo,
        data_publicacao,
        tipo_noticia_nome AS tipo_noticia,
        autor_nome
    FROM vw_noticias
    ORDER BY data_publicacao DESC, id_noticia DESC
""")

    context = {"noticias": noticias}
    return render(request, "noticias/lista.html", context)


def noticia_detalhe(request, noticia_id):
    noticia = _fetchone_dict("""
    SELECT
        id_noticia,
        titulo,
        conteudo,
        data_publicacao,
        tipo_noticia_nome AS tipo_noticia,
        autor_nome
    FROM vw_noticias
    WHERE id_noticia = %s
""", [noticia_id])

    if not noticia:
        messages.error(request, "Notícia não encontrada.")
        return redirect("noticias_lista")

    context = {"noticia": noticia}
    return render(request, "noticias/detalhe.html", context)


# ======================================================
#  CLIENTE – AS MINHAS ENCOMENDAS
# ======================================================

def minhas_encomendas(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para veres as tuas encomendas.")
        return redirect("login")

    encomendas = _fetchall_dicts("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda
        FROM vw_cliente_encomendas
        WHERE id_utilizador = %s
        ORDER BY data_encomenda DESC, id_encomenda DESC
    """, [user_id])

    encomendas_info = []
    for enc in encomendas:
        linhas = _fetchall_dicts("""
            SELECT
                id_encomenda,
                id_produto,
                nome_produto,
                preco_produto,
                quantidade
            FROM vw_cliente_encomenda_detalhe
            WHERE id_encomenda = %s
        """, [enc["id_encomenda"]])

        total = Decimal("0.00")
        for linha in linhas:
            if linha["preco_produto"] is not None:
                total += linha["preco_produto"] * linha["quantidade"]

        encomendas_info.append({
            "encomenda": enc,
            "total": total,
        })

    context = {"encomendas_info": encomendas_info}
    return render(request, "conta/minhas_encomendas.html", context)


def minha_encomenda_detail(request, encomenda_id):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão para veres as tuas encomendas.")
        return redirect("login")

    encomenda = _fetchone_dict("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda,
            id_utilizador
        FROM vw_cliente_encomendas
        WHERE id_encomenda = %s
          AND id_utilizador = %s
    """, [encomenda_id, user_id])

    if not encomenda:
        messages.error(request, "Encomenda não encontrada.")
        return redirect("minhas_encomendas")

    linhas = _fetchall_dicts("""
        SELECT
            id_encomenda,
            id_produto,
            nome_produto,
            preco_produto,
            quantidade
        FROM vw_cliente_encomenda_detalhe
        WHERE id_encomenda = %s
    """, [encomenda_id])

    total = Decimal("0.00")
    for linha in linhas:
        preco = linha.get("preco_produto")
        qtd = linha.get("quantidade") or 0

        if preco is None:
            linha["subtotal"] = Decimal("0.00")
            continue

    # garantir Decimal
    preco = Decimal(str(preco))
    qtd = int(qtd)

    linha["subtotal"] = preco * qtd
    total += linha["subtotal"]


    context = {"encomenda": encomenda, "linhas": linhas, "total_encomenda": total}
    return render(request, "conta/encomenda_detalhe.html", context)


# ======================================================
#  LOJA / CARRINHO – CLIENTE
# ======================================================

def loja_produtos(request):
    produtos = _fetchall_dicts("""
        SELECT
            id_produto,
            nome,
            descricao,
            preco,
            stock
        FROM vw_loja_produtos
        ORDER BY nome
    """)

    context = {"produtos": produtos}
    return render(request, "loja/produtos.html", context)


def loja_adicionar_produto(request, produto_id):
    if request.method != "POST":
        return redirect("loja_produtos")

    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    qtd_str = request.POST.get("quantidade", "1").strip()
    try:
        quantidade = int(qtd_str)
        if quantidade <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect("loja_produtos")

    ok, erro = _safe_callproc("sp_loja_adicionar_produto", [user_id, produto_id, quantidade])
    if not ok:
        messages.error(request, _user_friendly_db_error(erro))
    else:
        messages.success(request, "Produto adicionado ao carrinho.")

    return redirect("loja_carrinho")


def loja_carrinho(request):
    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    carrinho = _fetchone_dict("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda
        FROM vw_loja_carrinho
        WHERE id_utilizador = %s
    """, [user_id])

    linhas = []
    total = Decimal("0.00")

    if carrinho:
        linhas = _fetchall_dicts("""
            SELECT
                linha_id,
                id_encomenda,
                id_produto,
                nome_produto,
                preco_produto,
                quantidade
            FROM vw_loja_carrinho_linhas
            WHERE id_encomenda = %s
        """, [carrinho["id_encomenda"]])

        for linha in linhas:
            if linha["preco_produto"] is not None:
                total += linha["preco_produto"] * linha["quantidade"]

    context = {"carrinho": carrinho, "linhas": linhas, "total_encomenda": total}
    return render(request, "loja/carrinho.html", context)


def loja_remover_linha(request, produto_id):
    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    ok, erro = _safe_callproc(
        "sp_loja_remover_produto",
        [user_id, produto_id],
    )
    if not ok:
        messages.error(request, f"Não foi possível remover o produto do carrinho: {erro}")
    else:
        messages.success(request, "Produto removido do carrinho.")
    return redirect("loja_carrinho")



def loja_finalizar_encomenda(request):
    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    # Procedure só recebe (p_id_utilizador)
    ok, erro = _safe_callproc("sp_loja_finalizar_encomenda", [user_id])
    if not ok:
        messages.error(request, _user_friendly_db_error(erro))
        return redirect("loja_carrinho")

    messages.success(
        request,
        "Encomenda criada com sucesso! Podes acompanhar o estado em 'As minhas encomendas'."
    )
    return redirect("minhas_encomendas")

def cliente_cancelar_encomenda(request, encomenda_id):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect("login")

    if request.method != "POST":
        return redirect("minhas_encomendas")

    ok, erro = _safe_callproc("sp_cliente_cancelar_encomenda", [user_id, encomenda_id])
    if not ok:
        messages.error(request, f"Não foi possível cancelar a encomenda: {erro}")
    else:
        messages.success(request, "Encomenda cancelada com sucesso.")
    return redirect("minhas_encomendas")


def loja_remover_quantidade(request, produto_id):
    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    qtd_str = request.POST.get("quantidade_remover", "1").strip()
    try:
        qtd = int(qtd_str)
        if qtd <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade a remover inválida.")
        return redirect("loja_carrinho")

    ok, erro = _safe_callproc("sp_loja_diminuir_quantidade", [user_id, produto_id, qtd])
    if not ok:
        messages.error(request, _user_friendly_db_error(erro))
    else:
        messages.success(request, "Carrinho atualizado.")
    return redirect("loja_carrinho")


def loja_adicionar_quantidade(request, produto_id):
    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    qtd_str = request.POST.get("quantidade_adicionar", "1").strip()
    try:
        qtd = int(qtd_str)
        if qtd <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade a adicionar inválida.")
        return redirect("loja_carrinho")

    ok, erro = _safe_callproc("sp_loja_adicionar_produto", [user_id, produto_id, qtd])
    if not ok:
        messages.error(request, _user_friendly_db_error(erro))
    else:
        messages.success(request, "Carrinho atualizado.")
    return redirect("loja_carrinho")
def loja_adicionar_quantidade(request, produto_id):
    user_id = _require_cliente(request)
    if user_id is None:
        return redirect("login")

    if request.method != "POST":
        return redirect("loja_carrinho")

    qtd_str = request.POST.get("quantidade_adicionar", "1").strip()
    try:
        qtd = int(qtd_str)
        if qtd <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade a adicionar inválida.")
        return redirect("loja_carrinho")

    ok, erro = _safe_callproc("sp_loja_adicionar_produto", [user_id, produto_id, qtd])
    if not ok:
        messages.error(request, f"Não foi possível atualizar o carrinho: {erro}")
    else:
        messages.success(request, "Carrinho atualizado.")
    return redirect("loja_carrinho")

def area_utilizador(request):
    user_id = request.session.get("user_id")
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect("login")

    perfil = _fetchone_dict("""
        SELECT id_utilizador, nome, email, morada, nif, tipo_designacao
        FROM vw_conta_perfil
        WHERE id_utilizador = %s
    """, [user_id])

    context = {
        "perfil": perfil,
        "user_tipo": user_tipo,
    }
    return render(request, "conta/area.html", context)


def conta_editar_perfil(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect("login")

    perfil = _fetchone_dict("""
        SELECT id_utilizador, nome, email, morada, nif, tipo_designacao
        FROM vw_conta_perfil
        WHERE id_utilizador = %s
    """, [user_id])

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        nif = request.POST.get("nif", "").strip()
        morada = request.POST.get("morada", "").strip()

        ok, erro = _safe_callproc("sp_utilizador_atualizar_perfil", [user_id, nome, email, morada or None, nif])
        if not ok:
            messages.error(request, f"Erro ao atualizar perfil: {erro}")
        else:
            # atualizar também a sessão (para o header)
            request.session["user_nome"] = nome
            request.session["user_email"] = email
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("area_utilizador")

    return render(request, "conta/perfil_form.html", {"perfil": perfil})


def conta_alterar_password(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect("login")

    # buscar hash atual para validar password atual
    row = _fetchone_dict("SELECT password FROM Utilizador WHERE id_utilizador = %s", [user_id])
    current_hash = (row or {}).get("password")

    if request.method == "POST":
        atual = request.POST.get("password_atual", "")
        nova = request.POST.get("password_nova", "")
        nova2 = request.POST.get("password_nova2", "")

        if not nova:
            messages.error(request, "A nova password é obrigatória.")
        elif nova != nova2:
            messages.error(request, "As novas passwords não coincidem.")
        else:
            # validar password atual
            try:
                ok_atual = check_password(atual, current_hash or "")
            except ValueError:
                ok_atual = False

            if not ok_atual:
                messages.error(request, "Password atual incorreta.")
            else:
                nova_hash = make_password(nova)
                ok, erro = _safe_callproc("sp_utilizador_alterar_password", [user_id, nova_hash])
                if not ok:
                    messages.error(request, f"Erro ao alterar password: {erro}")
                else:
                    messages.success(request, "Password alterada com sucesso.")
                    return redirect("area_utilizador")

    return render(request, "conta/password_form.html")

def fornecedor_encomendas_list(request):
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if user_tipo != "fornecedor":
        messages.error(request, "Apenas utilizadores do tipo Fornecedor podem aceder a esta área.")
        return redirect("home")

    user_email = request.session.get("user_email")

    fornecedor = _fetchone_dict("""
        SELECT id_fornecedor, nome, email
        FROM vw_fornecedores
        WHERE LOWER(email) = LOWER(%s)
    """, [user_email])

    if not fornecedor:
        messages.error(request, "Não foi encontrado fornecedor associado ao teu email.")
        return redirect("home")

    encomendas = _fetchall_dicts("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda,
            cliente_nome,
            cliente_email,
            total_fornecedor
        FROM vw_fornecedor_encomendas
        WHERE id_fornecedor = %s
        ORDER BY data_encomenda DESC, id_encomenda DESC
    """, [fornecedor["id_fornecedor"]])

    return render(request, "fornecedor/encomendas/list.html", {
        "fornecedor": fornecedor,
        "encomendas": encomendas,
    })


def fornecedor_encomenda_detail(request, encomenda_id):
    user_tipo = (request.session.get("user_tipo") or "").lower()
    if user_tipo != "fornecedor":
        messages.error(request, "Apenas utilizadores do tipo Fornecedor podem aceder a esta área.")
        return redirect("home")

    user_email = request.session.get("user_email")

    fornecedor = _fetchone_dict("""
        SELECT id_fornecedor, nome, email
        FROM vw_fornecedores
        WHERE LOWER(email) = LOWER(%s)
    """, [user_email])

    if not fornecedor:
        messages.error(request, "Não foi encontrado fornecedor associado ao teu email.")
        return redirect("home")

    encomenda = _fetchone_dict("""
        SELECT
            id_encomenda,
            data_encomenda,
            estado_encomenda,
            cliente_nome,
            cliente_email,
            total_fornecedor
        FROM vw_fornecedor_encomendas
        WHERE id_fornecedor = %s
          AND id_encomenda = %s
    """, [fornecedor["id_fornecedor"], encomenda_id])

    if not encomenda:
        messages.error(request, "Encomenda não encontrada (ou não contém produtos teus).")
        return redirect("fornecedor_encomendas_list")

    linhas = _fetchall_dicts("""
        SELECT
            id_produto,
            nome_produto,
            preco_produto,
            quantidade,
            subtotal
        FROM vw_fornecedor_encomenda_linhas
        WHERE id_fornecedor = %s
          AND id_encomenda = %s
        ORDER BY nome_produto
    """, [fornecedor["id_fornecedor"], encomenda_id])

    return render(request, "fornecedor/encomendas/detail.html", {
        "fornecedor": fornecedor,
        "encomenda": encomenda,
        "linhas": linhas,
    })
