"""Regra de negócio de relatório de vendas — fora dos controllers e models de dados."""

# Faixas de desconto sobre o faturamento (constantes nomeadas, sem magic numbers).
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]


def compute_discount(faturamento):
    for threshold, rate in DISCOUNT_TIERS:
        if faturamento > threshold:
            return round(faturamento * rate, 2)
    return 0.0


class RelatorioService:
    def __init__(self, db):
        self.db = db

    def sales_report(self):
        cursor = self.db.cursor()
        # Agregações feitas no banco (sem laços Python / sem N+1).
        cursor.execute(
            """
            SELECT
                COUNT(*)                                            AS total_pedidos,
                COALESCE(SUM(total), 0)                             AS faturamento,
                COALESCE(SUM(status = 'pendente'), 0)              AS pendentes,
                COALESCE(SUM(status = 'aprovado'), 0)              AS aprovados,
                COALESCE(SUM(status = 'cancelado'), 0)             AS cancelados
            FROM pedidos
            """
        )
        row = cursor.fetchone()
        total_pedidos = row["total_pedidos"]
        faturamento = row["faturamento"]
        desconto = compute_discount(faturamento)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": row["pendentes"],
            "pedidos_aprovados": row["aprovados"],
            "pedidos_cancelados": row["cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos else 0,
        }
