"""Views/Routes de Task — apenas mapeiam caminho → controller."""
from flask import Blueprint

from controllers import task_controller as ctrl

task_bp = Blueprint("tasks", __name__)

task_bp.add_url_rule("/tasks", "get_tasks", ctrl.list_tasks, methods=["GET"])
task_bp.add_url_rule("/tasks/<int:task_id>", "get_task", ctrl.get_task, methods=["GET"])
task_bp.add_url_rule("/tasks", "create_task", ctrl.create_task, methods=["POST"])
task_bp.add_url_rule("/tasks/<int:task_id>", "update_task", ctrl.update_task, methods=["PUT"])
task_bp.add_url_rule("/tasks/<int:task_id>", "delete_task", ctrl.delete_task, methods=["DELETE"])
task_bp.add_url_rule("/tasks/search", "search_tasks", ctrl.search_tasks, methods=["GET"])
task_bp.add_url_rule("/tasks/stats", "task_stats", ctrl.task_stats, methods=["GET"])
