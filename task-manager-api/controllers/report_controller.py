"""Controller de Relatórios e Categorias — delega agregações ao ReportService."""
import logging

from flask import jsonify, request

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.report_service import ReportService

logger = logging.getLogger("reports")
_report_service = ReportService()


def summary_report():
    return jsonify(_report_service.summary()), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(_report_service.user_report(user)), 200


def list_categories():
    result = []
    for c in Category.query.all():
        data = c.to_dict()
        data["task_count"] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", "#000000")
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception:
        db.session.rollback()
        logger.exception("erro ao criar categoria")
        return jsonify({"error": "Erro ao criar categoria"}), 500


def update_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({"error": "Categoria não encontrada"}), 404
    data = request.get_json()
    if "name" in data:
        cat.name = data["name"]
    if "description" in data:
        cat.description = data["description"]
    if "color" in data:
        cat.color = data["color"]
    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except Exception:
        db.session.rollback()
        logger.exception("erro ao atualizar categoria")
        return jsonify({"error": "Erro ao atualizar"}), 500


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({"error": "Categoria não encontrada"}), 404
    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({"message": "Categoria deletada"}), 200
    except Exception:
        db.session.rollback()
        logger.exception("erro ao deletar categoria")
        return jsonify({"error": "Erro ao deletar"}), 500
