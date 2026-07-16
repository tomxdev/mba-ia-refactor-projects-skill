"""Notificações centralizadas via logger (substitui os print() espalhados)."""
import logging

logger = logging.getLogger("notifications")


class NotificationService:
    def order_created(self, pedido_id, usuario_id):
        logger.info("pedido %s criado para usuário %s", pedido_id, usuario_id)

    def order_status_changed(self, pedido_id, status):
        if status == "aprovado":
            logger.info("pedido %s aprovado — preparar envio", pedido_id)
        elif status == "cancelado":
            logger.info("pedido %s cancelado — devolver estoque", pedido_id)
