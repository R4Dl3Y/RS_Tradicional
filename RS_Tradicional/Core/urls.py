from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),

    # ADMIN – PRODUTOS
    path("admin/produtos/", views.admin_product_list, name="admin_product_list"),
    path("admin/produtos/novo/", views.admin_product_create, name="admin_product_create"),
    path("admin/produtos/<int:produto_id>/editar/", views.admin_product_edit, name="admin_product_edit"),
    path("admin/produtos/<int:produto_id>/remover/", views.admin_product_delete, name="admin_product_delete"),
    path("admin/produtos/pendentes/", views.admin_product_pending_list, name="admin_product_pending_list"),
    path("admin/produtos/<int:produto_id>/aprovar/", views.admin_product_approve, name="admin_product_approve"),
    path("admin/produtos/<int:produto_id>/rejeitar/", views.admin_product_reject, name="admin_product_reject"),

    # ADMIN – TIPOS DE PRODUTO
    path("admin/tipos-produto/", views.admin_tipo_produto_list, name="admin_tipo_produto_list"),
    path("admin/tipos-produto/novo/", views.admin_tipo_produto_create, name="admin_tipo_produto_create"),
    path("admin/tipos-produto/<int:tipo_id>/editar/", views.admin_tipo_produto_edit, name="admin_tipo_produto_edit"),
    path("admin/tipos-produto/<int:tipo_id>/remover/", views.admin_tipo_produto_delete, name="admin_tipo_produto_delete"),

    # ADMIN – FORNECEDORES
    path("admin/fornecedores/", views.admin_fornecedor_list, name="admin_fornecedor_list"),
    path("admin/fornecedores/novo/", views.admin_fornecedor_create, name="admin_fornecedor_create"),
    path("admin/fornecedores/<int:fornecedor_id>/editar/", views.admin_fornecedor_edit, name="admin_fornecedor_edit"),
    path("admin/fornecedores/<int:fornecedor_id>/remover/", views.admin_fornecedor_delete, name="admin_fornecedor_delete"),
    path("fornecedor/produtos/novo/", views.fornecedor_product_create, name="fornecedor_product_create"),
    path("fornecedor/produtos/", views.fornecedor_product_list, name="fornecedor_product_list"),

    # ADMIN – TIPOS DE UTILIZADOR
    path("admin/tipos-utilizador/", views.admin_tipo_utilizador_list, name="admin_tipo_utilizador_list"),
    path("admin/tipos-utilizador/novo/", views.admin_tipo_utilizador_create, name="admin_tipo_utilizador_create"),
    path("admin/tipos-utilizador/<int:tipo_id>/editar/", views.admin_tipo_utilizador_edit, name="admin_tipo_utilizador_edit"),
    path("admin/tipos-utilizador/<int:tipo_id>/remover/", views.admin_tipo_utilizador_delete, name="admin_tipo_utilizador_delete"),

    # ADMIN – UTILIZADORES
    path("admin/utilizadores/", views.admin_user_list, name="admin_user_list"),
    path("admin/utilizadores/novo/", views.admin_user_create, name="admin_user_create"),
    path("admin/utilizadores/<int:user_id>/editar/", views.admin_user_edit, name="admin_user_edit"),
    path("admin/utilizadores/<int:user_id>/remover/", views.admin_user_delete, name="admin_user_delete"),

    # ADMIN – ENCOMENDAS
    path("admin/encomendas/", views.admin_encomenda_list, name="admin_encomenda_list"),
    path("admin/encomendas/novo/", views.admin_encomenda_create, name="admin_encomenda_create"),
    path("admin/encomendas/<int:encomenda_id>/editar/", views.admin_encomenda_edit, name="admin_encomenda_edit"),
    path("admin/encomendas/<int:encomenda_id>/remover/", views.admin_encomenda_delete, name="admin_encomenda_delete"),
    path("admin/encomendas/<int:encomenda_id>/detalhe/", views.admin_encomenda_detail, name="admin_encomenda_detail"),
    path("admin/encomendas/<int:encomenda_id>/linhas/adicionar/", views.admin_encomenda_add_item, name="admin_encomenda_add_item"),
    path("admin/encomendas/<int:encomenda_id>/linhas/<int:produto_id>/atualizar/", views.admin_encomenda_update_item, name="admin_encomenda_update_item"),
    path("admin/encomendas/<int:encomenda_id>/linhas/<int:produto_id>/remover/", views.admin_encomenda_delete_item, name="admin_encomenda_delete_item"),


    # ADMIN – NOTÍCIAS
    path("admin/noticias/", views.admin_noticia_list, name="admin_noticia_list"),
    path("admin/noticias/novo/", views.admin_noticia_create, name="admin_noticia_create"),
    path("admin/noticias/<int:noticia_id>/editar/", views.admin_noticia_edit, name="admin_noticia_edit"),
    path("admin/noticias/<int:noticia_id>/remover/", views.admin_noticia_delete, name="admin_noticia_delete"),

    path("conta/", views.area_utilizador, name="area_utilizador"),
    path("conta/perfil/", views.conta_editar_perfil, name="conta_editar_perfil"),
    path("conta/password/", views.conta_alterar_password, name="conta_alterar_password"),
    path("conta/encomendas/", views.minhas_encomendas, name="minhas_encomendas"),
    path("conta/encomendas/<int:encomenda_id>/", views.minha_encomenda_detail, name="minha_encomenda_detail"),
    path("conta/encomendas/<int:encomenda_id>/cancelar/", views.cliente_cancelar_encomenda, name="cliente_cancelar_encomenda"),


    # LOJA / CLIENTE
    path("loja/", views.loja_produtos, name="loja_produtos"),
    path("loja/adicionar/<int:produto_id>/", views.loja_adicionar_produto, name="loja_adicionar_produto"),
    path("loja/carrinho/", views.loja_carrinho, name="loja_carrinho"),
   # path("loja/carrinho/remover/<int:produto_id>/", views.loja_remover_linha, name="loja_remover_linha"),
    path("loja/carrinho/finalizar/", views.loja_finalizar_encomenda, name="loja_finalizar_encomenda"),
    path("loja/carrinho/remover/<int:produto_id>/", views.loja_remover_quantidade, name="loja_remover_quantidade"),
    path("loja/carrinho/adicionar/<int:produto_id>/", views.loja_adicionar_quantidade, name="loja_adicionar_quantidade"),



    # NOTÍCIAS – CLIENTE
    path("noticias/", views.noticias_lista, name="noticias_lista"),
    path("noticias/<int:noticia_id>/", views.noticia_detalhe, name="noticia_detalhe"),
    
    path("fornecedor/encomendas/", views.fornecedor_encomendas_list, name="fornecedor_encomendas_list"),
    path("fornecedor/encomendas/<int:encomenda_id>/", views.fornecedor_encomenda_detail, name="fornecedor_encomenda_detail"),
]
