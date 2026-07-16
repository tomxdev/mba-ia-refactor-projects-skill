"""Views/Routes de Usuário — apenas mapeiam caminho → controller."""
from flask import Blueprint

from controllers import user_controller as ctrl

user_bp = Blueprint("users", __name__)

user_bp.add_url_rule("/users", "get_users", ctrl.list_users, methods=["GET"])
user_bp.add_url_rule("/users/<int:user_id>", "get_user", ctrl.get_user, methods=["GET"])
user_bp.add_url_rule("/users", "create_user", ctrl.create_user, methods=["POST"])
user_bp.add_url_rule("/users/<int:user_id>", "update_user", ctrl.update_user, methods=["PUT"])
user_bp.add_url_rule("/users/<int:user_id>", "delete_user", ctrl.delete_user, methods=["DELETE"])
user_bp.add_url_rule("/users/<int:user_id>/tasks", "get_user_tasks", ctrl.get_user_tasks, methods=["GET"])
user_bp.add_url_rule("/login", "login", ctrl.login, methods=["POST"])
