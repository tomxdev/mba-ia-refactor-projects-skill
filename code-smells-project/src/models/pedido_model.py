"""Model de Pedido — SQL parametrizado e leitura de itens sem N+1."""


class PedidoModel:
    def __init__(self, db):
        self.db = db

    def create(self, usuario_id, itens):
        cursor = self.db.cursor()

        # Carrega todos os produtos do pedido em UMA query (evita N+1).
        ids = [item["produto_id"] for item in itens]
        placeholders = ",".join("?" * len(ids))
        cursor.execute(
            f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})",
            ids,
        )
        produtos = {row["id"]: row for row in cursor.fetchall()}

        total = 0
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                return {"erro": f"Produto {item['produto_id']} não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {produto['nome']}"}
            total += produto["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = produtos[item["produto_id"]]
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        self.db.commit()
        return {"pedido_id": pedido_id, "total": total}

    def _hydrate(self, pedidos):
        """Anexa os itens a cada pedido usando uma única query (sem N+1)."""
        if not pedidos:
            return []
        by_id = {p["id"]: {**p, "itens": []} for p in pedidos}
        placeholders = ",".join("?" * len(by_id))
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
            "p.nome AS produto_nome "
            "FROM itens_pedido ip LEFT JOIN produtos p ON p.id = ip.produto_id "
            f"WHERE ip.pedido_id IN ({placeholders})",
            list(by_id.keys()),
        )
        for item in cursor.fetchall():
            by_id[item["pedido_id"]]["itens"].append(
                {
                    "produto_id": item["produto_id"],
                    "produto_nome": item["produto_nome"] or "Desconhecido",
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"],
                }
            )
        return list(by_id.values())

    def _rows(self, cursor):
        return [
            {
                "id": r["id"],
                "usuario_id": r["usuario_id"],
                "status": r["status"],
                "total": r["total"],
                "criado_em": r["criado_em"],
            }
            for r in cursor.fetchall()
        ]

    def get_by_usuario(self, usuario_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return self._hydrate(self._rows(cursor))

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM pedidos")
        return self._hydrate(self._rows(cursor))

    def update_status(self, pedido_id, novo_status):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
        )
        self.db.commit()
        return True
