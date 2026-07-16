"""Controller de Produto — orquestra entrada/validação/resposta, delega ao model."""
from flask import jsonify, request

from validators.produto_validator import validate_produto


class ProdutoController:
    def __init__(self, model):
        self.model = model

    def listar(self):
        return jsonify({"dados": self.model.get_all(), "sucesso": True}), 200

    def buscar(self, id):
        produto = self.model.get_by_id(id)
        if produto:
            return jsonify({"dados": produto, "sucesso": True}), 200
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404

    def criar(self):
        campos, erro = validate_produto(request.get_json())
        if erro:
            return jsonify({"erro": erro}), 400
        novo_id = self.model.create(**campos)
        return jsonify(
            {"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}
        ), 201

    def atualizar(self, id):
        if not self.model.get_by_id(id):
            return jsonify({"erro": "Produto não encontrado"}), 404
        campos, erro = validate_produto(request.get_json(), checar_categoria=False)
        if erro:
            return jsonify({"erro": erro}), 400
        self.model.update(id, **campos)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, id):
        if not self.model.get_by_id(id):
            return jsonify({"erro": "Produto não encontrado"}), 404
        self.model.delete(id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

    def buscar_query(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)
        preco_min = float(preco_min) if preco_min else None
        preco_max = float(preco_max) if preco_max else None
        resultados = self.model.search(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
