"""Tratamento de erro centralizado — respostas padronizadas, sem vazar stack."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("errors")


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Preserva o comportamento HTTP padrão (404, 405, ...).
        if isinstance(e, HTTPException):
            return jsonify({"erro": e.description}), e.code
        logger.exception("erro não tratado: %s", e)
        return jsonify({"erro": "Erro interno"}), 500
