"""Controller de Task — orquestra validação, persistência e serialização."""
import logging
from datetime import datetime

from flask import jsonify, request

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import VALID_STATUSES, is_overdue, now_utc
from utils.serializers import serialize_task

logger = logging.getLogger("tasks")


def _load_lookup_maps():
    users_by_id = {u.id: u for u in User.query.all()}
    categories_by_id = {c.id: c for c in Category.query.all()}
    return users_by_id, categories_by_id


def list_tasks():
    # Pré-carrega usuários e categorias uma vez (evita N+1 por task).
    users_by_id, categories_by_id = _load_lookup_maps()
    tasks = Task.query.all()
    result = [serialize_task(t, users_by_id, categories_by_id) for t in tasks]
    return jsonify(result), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    data = task.to_dict()
    data["overdue"] = is_overdue(task.due_date, task.status)
    return jsonify(data), 200


def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    title = data.get("title")
    if not title:
        return jsonify({"error": "Título é obrigatório"}), 400
    if len(title) < 3:
        return jsonify({"error": "Título muito curto"}), 400
    if len(title) > 200:
        return jsonify({"error": "Título muito longo"}), 400

    status = data.get("status", "pending")
    priority = data.get("priority", 3)
    if status not in VALID_STATUSES:
        return jsonify({"error": "Status inválido"}), 400
    if priority < 1 or priority > 5:
        return jsonify({"error": "Prioridade deve ser entre 1 e 5"}), 400

    user_id = data.get("user_id")
    category_id = data.get("category_id")
    if user_id and not db.session.get(User, user_id):
        return jsonify({"error": "Usuário não encontrado"}), 404
    if category_id and not db.session.get(Category, category_id):
        return jsonify({"error": "Categoria não encontrada"}), 404

    task = Task()
    task.title = title
    task.description = data.get("description", "")
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get("due_date")
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    tags = data.get("tags")
    if tags:
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception:
        db.session.rollback()
        logger.exception("erro ao criar task")
        return jsonify({"error": "Erro ao criar task"}), 500


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "title" in data:
        if len(data["title"]) < 3:
            return jsonify({"error": "Título muito curto"}), 400
        if len(data["title"]) > 200:
            return jsonify({"error": "Título muito longo"}), 400
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": "Status inválido"}), 400
        task.status = data["status"]
    if "priority" in data:
        if data["priority"] < 1 or data["priority"] > 5:
            return jsonify({"error": "Prioridade deve ser entre 1 e 5"}), 400
        task.priority = data["priority"]
    if "user_id" in data:
        if data["user_id"] and not db.session.get(User, data["user_id"]):
            return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = data["user_id"]
    if "category_id" in data:
        if data["category_id"] and not db.session.get(Category, data["category_id"]):
            return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = data["category_id"]
    if "due_date" in data:
        if data["due_date"]:
            try:
                task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Formato de data inválido"}), 400
        else:
            task.due_date = None
    if "tags" in data:
        tags = data["tags"]
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception:
        db.session.rollback()
        logger.exception("erro ao atualizar task")
        return jsonify({"error": "Erro ao atualizar"}), 500


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deletada com sucesso"}), 200
    except Exception:
        db.session.rollback()
        logger.exception("erro ao deletar task")
        return jsonify({"error": "Erro ao deletar"}), 500


def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%"))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return jsonify([t.to_dict() for t in tasks.all()]), 200


def task_stats():
    total = Task.query.count()
    by_status = {
        s: Task.query.filter_by(status=s).count() for s in VALID_STATUSES
    }
    overdue_count = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < now_utc(),
        Task.status.notin_(["done", "cancelled"]),
    ).count()

    return jsonify(
        {
            "total": total,
            "pending": by_status["pending"],
            "in_progress": by_status["in_progress"],
            "done": by_status["done"],
            "cancelled": by_status["cancelled"],
            "overdue": overdue_count,
            "completion_rate": round((by_status["done"] / total) * 100, 2) if total else 0,
        }
    ), 200
