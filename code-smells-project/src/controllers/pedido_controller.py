"""Controller de Pedido — orquestra criação, listagem, status e relatório."""
from flask import jsonify, request

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


class PedidoController:
    def __init__(self, model, relatorio_service, notification_service):
        self.model = model
        self.relatorio_service = relatorio_service
        self.notifications = notification_service

    def criar(self):
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

        resultado = self.model.create(usuario_id, itens)
        if "erro" in resultado:
            return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

        self.notifications.order_created(resultado["pedido_id"], usuario_id)
        return jsonify(
            {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}
        ), 201

    def listar_por_usuario(self, usuario_id):
        return jsonify({"dados": self.model.get_by_usuario(usuario_id), "sucesso": True}), 200

    def listar_todos(self):
        return jsonify({"dados": self.model.get_all(), "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        dados = request.get_json()
        novo_status = dados.get("status", "") if dados else ""
        if novo_status not in STATUS_VALIDOS:
            return jsonify({"erro": "Status inválido"}), 400
        self.model.update_status(pedido_id, novo_status)
        self.notifications.order_status_changed(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

    def relatorio_vendas(self):
        return jsonify({"dados": self.relatorio_service.sales_report(), "sucesso": True}), 200
