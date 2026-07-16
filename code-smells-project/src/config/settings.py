"""Configuração central da aplicação — segredos vêm do ambiente, nunca do código."""
import os
import secrets


class Settings:
    # Nunca hardcoded: usa a env var, ou gera uma chave efêmera para dev/local.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    # DEBUG desligado por padrão (seguro para produção).
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    # Token exigido para operações administrativas destrutivas.
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
