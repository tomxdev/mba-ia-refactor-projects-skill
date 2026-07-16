"""Views/Routes de Relatórios e Categorias — apenas mapeiam caminho → controller."""
from flask import Blueprint

from controllers import report_controller as ctrl

report_bp = Blueprint("reports", __name__)

report_bp.add_url_rule("/reports/summary", "summary_report", ctrl.summary_report, methods=["GET"])
report_bp.add_url_rule("/reports/user/<int:user_id>", "user_report", ctrl.user_report, methods=["GET"])
report_bp.add_url_rule("/categories", "get_categories", ctrl.list_categories, methods=["GET"])
report_bp.add_url_rule("/categories", "create_category", ctrl.create_category, methods=["POST"])
report_bp.add_url_rule("/categories/<int:cat_id>", "update_category", ctrl.update_category, methods=["PUT"])
report_bp.add_url_rule("/categories/<int:cat_id>", "delete_category", ctrl.delete_category, methods=["DELETE"])
