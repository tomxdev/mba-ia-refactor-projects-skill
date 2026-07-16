"""Views/Routes — apenas mapeiam método+caminho → método do controller.

Nenhuma regra de negócio ou SQL aqui. Os controllers são injetados.
"""
from flask import Blueprint


def build_blueprint(produto_c, usuario_c, pedido_c, system_c):
    bp = Blueprint("api", __name__)

    # Produtos
    bp.add_url_rule("/produtos", "listar_produtos", produto_c.listar, methods=["GET"])
    bp.add_url_rule("/produtos/busca", "buscar_produtos", produto_c.buscar_query, methods=["GET"])
    bp.add_url_rule("/produtos/<int:id>", "buscar_produto", produto_c.buscar, methods=["GET"])
    bp.add_url_rule("/produtos", "criar_produto", produto_c.criar, methods=["POST"])
    bp.add_url_rule("/produtos/<int:id>", "atualizar_produto", produto_c.atualizar, methods=["PUT"])
    bp.add_url_rule("/produtos/<int:id>", "deletar_produto", produto_c.deletar, methods=["DELETE"])

    # Usuários / auth
    bp.add_url_rule("/usuarios", "listar_usuarios", usuario_c.listar, methods=["GET"])
    bp.add_url_rule("/usuarios/<int:id>", "buscar_usuario", usuario_c.buscar, methods=["GET"])
    bp.add_url_rule("/usuarios", "criar_usuario", usuario_c.criar, methods=["POST"])
    bp.add_url_rule("/login", "login", usuario_c.login, methods=["POST"])

    # Pedidos
    bp.add_url_rule("/pedidos", "criar_pedido", pedido_c.criar, methods=["POST"])
    bp.add_url_rule("/pedidos", "listar_todos_pedidos", pedido_c.listar_todos, methods=["GET"])
    bp.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>",
        "listar_pedidos_usuario",
        pedido_c.listar_por_usuario,
        methods=["GET"],
    )
    bp.add_url_rule(
        "/pedidos/<int:pedido_id>/status",
        "atualizar_status_pedido",
        pedido_c.atualizar_status,
        methods=["PUT"],
    )

    # Relatórios
    bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", pedido_c.relatorio_vendas, methods=["GET"])

    # Sistema
    bp.add_url_rule("/", "index", system_c.index, methods=["GET"])
    bp.add_url_rule("/health", "health_check", system_c.health, methods=["GET"])
    bp.add_url_rule("/admin/reset-db", "reset_db", system_c.reset_db, methods=["POST"])

    return bp
