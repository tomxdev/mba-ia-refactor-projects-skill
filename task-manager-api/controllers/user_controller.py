"""Controller de Usuário — cadastro, atualização, deleção e login."""
import logging

from flask import jsonify, request

from database import db
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email
from utils.serializers import serialize_task

logger = logging.getLogger("users")


def list_users():
    users = User.query.all()
    result = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "active": u.active,
            "created_at": str(u.created_at),
            "task_count": len(u.tasks),
        }
        for u in users
    ]
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data["tasks"] = [t.to_dict() for t in tasks]
    return jsonify(data), 200


def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400
    if not password:
        return jsonify({"error": "Senha é obrigatória"}), 400
    if not validate_email(email):
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": "Senha deve ter no mínimo 4 caracteres"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409
    if role not in VALID_ROLES:
        return jsonify({"error": "Role inválido"}), 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception:
        db.session.rollback()
        logger.exception("erro ao criar usuário")
        return jsonify({"error": "Erro ao criar usuário"}), 500


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        if not validate_email(data["email"]):
            return jsonify({"error": "Email inválido"}), 400
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = data["email"]
    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            return jsonify({"error": "Senha muito curta"}), 400
        user.set_password(data["password"])
    if "role" in data:
        if data["role"] not in VALID_ROLES:
            return jsonify({"error": "Role inválido"}), 400
        user.role = data["role"]
    if "active" in data:
        user.active = data["active"]

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception:
        db.session.rollback()
        logger.exception("erro ao atualizar usuário")
        return jsonify({"error": "Erro ao atualizar"}), 500


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    except Exception:
        db.session.rollback()
        logger.exception("erro ao deletar usuário")
        return jsonify({"error": "Erro ao deletar"}), 500


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        data = serialize_task(t)
        # Preserva o subconjunto de campos do endpoint original.
        result.append(
            {
                "id": data["id"],
                "title": data["title"],
                "description": data["description"],
                "status": data["status"],
                "priority": data["priority"],
                "created_at": data["created_at"],
                "due_date": data["due_date"],
                "overdue": data["overdue"],
            }
        )
    return jsonify(result), 200


def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401
    if not user.active:
        return jsonify({"error": "Usuário inativo"}), 403

    return jsonify(
        {
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "token": "fake-jwt-token-" + str(user.id),
        }
    ), 200
