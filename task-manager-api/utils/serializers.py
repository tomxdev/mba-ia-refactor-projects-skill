"""Serialização de Task — evita duplicar a montagem de dicts nas rotas."""
from utils.helpers import is_overdue


def serialize_task(task, users_by_id=None, categories_by_id=None):
    """Serializa a task com o campo `overdue`. Se os mapas forem fornecidos,
    inclui `user_name`/`category_name` sem disparar N+1."""
    data = task.to_dict()
    data["overdue"] = is_overdue(task.due_date, task.status)
    if users_by_id is not None:
        user = users_by_id.get(task.user_id)
        data["user_name"] = user.name if user else None
    if categories_by_id is not None:
        category = categories_by_id.get(task.category_id)
        data["category_name"] = category.name if category else None
    return data
