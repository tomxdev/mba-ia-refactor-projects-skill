"""Tratamento de erro centralizado — respostas padronizadas."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("errors")


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": e.description}), e.code
        logger.exception("erro não tratado: %s", e)
        return jsonify({"error": "Erro interno"}), 500
