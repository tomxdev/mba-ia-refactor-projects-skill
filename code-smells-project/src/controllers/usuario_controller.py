"""Controller de Usuário — autenticação e cadastro."""
from flask import jsonify, request


class UsuarioController:
    def __init__(self, model):
        self.model = model

    def listar(self):
        return jsonify({"dados": self.model.get_all(), "sucesso": True}), 200

    def buscar(self, id):
        usuario = self.model.get_by_id(id)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True}), 200
        return jsonify({"erro": "Usuário não encontrado"}), 404

    def criar(self):
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
        novo_id = self.model.create(nome, email, senha)
        return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201

    def login(self):
        dados = request.get_json()
        email = dados.get("email", "") if dados else ""
        senha = dados.get("senha", "") if dados else ""
        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
        usuario = self.model.authenticate(email, senha)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
