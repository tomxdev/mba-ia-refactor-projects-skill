"""Helpers utilitários — fonte única para tempo UTC e regra de 'overdue'."""
import re
import uuid
from datetime import datetime, timezone

# Constantes de domínio (evita magic strings/numbers espalhados).
VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"
EMAIL_REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"


def now_utc():
    """UTC 'naive' — moderno (sem datetime.utcnow deprecated) e compatível
    com as colunas DateTime existentes (que são naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_overdue(due_date, status):
    """Regra única de atraso, reutilizada por models, controllers e relatórios."""
    return bool(
        due_date
        and due_date < now_utc()
        and status not in ("done", "cancelled")
    )


def validate_email(email):
    return bool(email and re.match(EMAIL_REGEX, email))


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if not total:
        return 0
    return round((part / total) * 100, 2)


def generate_id():
    return str(uuid.uuid4())
