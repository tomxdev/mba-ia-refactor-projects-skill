"""Controller de sistema — index, health check e operações administrativas."""
from flask import jsonify, request


class SystemController:
    def __init__(self, db, admin_token=None):
        self.db = db
        self.admin_token = admin_token

    def index(self):
        return jsonify(
            {
                "mensagem": "Bem-vindo à API da Loja",
                "versao": "1.0.0",
                "endpoints": {
                    "produtos": "/produtos",
                    "usuarios": "/usuarios",
                    "pedidos": "/pedidos",
                    "login": "/login",
                    "relatorios": "/relatorios/vendas",
                    "health": "/health",
                },
            }
        )

    def health(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]
        # Sem segredos no payload (o original vazava SECRET_KEY aqui).
        return jsonify(
            {
                "status": "ok",
                "database": "connected",
                "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
                "versao": "1.0.0",
            }
        ), 200

    def reset_db(self):
        # Operação destrutiva: exige token administrativo (antes era aberta).
        if not self.admin_token or request.headers.get("X-Admin-Token") != self.admin_token:
            return jsonify({"erro": "Não autorizado"}), 401
        cursor = self.db.cursor()
        for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            cursor.execute(f"DELETE FROM {tabela}")
        self.db.commit()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
