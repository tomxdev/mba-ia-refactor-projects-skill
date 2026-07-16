"""Serviço de relatórios — agregações no banco (elimina o N+1 das rotas)."""
from datetime import timedelta

from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import is_overdue, now_utc


class ReportService:
    def summary(self):
        now = now_utc()
        total_tasks = db.session.query(func.count(Task.id)).scalar()
        total_users = db.session.query(func.count(User.id)).scalar()
        total_categories = db.session.query(func.count(Category.id)).scalar()

        status_counts = dict(
            db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        )
        priority_counts = dict(
            db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
        )

        overdue_tasks = (
            db.session.query(Task)
            .filter(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status.notin_(["done", "cancelled"]),
            )
            .all()
        )
        overdue_list = [
            {
                "id": t.id,
                "title": t.title,
                "due_date": str(t.due_date),
                "days_overdue": (now - t.due_date).days,
            }
            for t in overdue_tasks
        ]

        seven_days_ago = now - timedelta(days=7)
        recent_tasks = (
            db.session.query(func.count(Task.id))
            .filter(Task.created_at >= seven_days_ago)
            .scalar()
        )
        recent_done = (
            db.session.query(func.count(Task.id))
            .filter(Task.status == "done", Task.updated_at >= seven_days_ago)
            .scalar()
        )

        # Produtividade por usuário em UMA query agregada (antes era N+1).
        rows = (
            db.session.query(
                User.id,
                User.name,
                func.count(Task.id),
                func.sum(case((Task.status == "done", 1), else_=0)),
            )
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id, User.name)
            .all()
        )
        user_stats = []
        for uid, uname, total, completed in rows:
            total = total or 0
            completed = completed or 0
            user_stats.append(
                {
                    "user_id": uid,
                    "user_name": uname,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": round((completed / total) * 100, 2) if total else 0,
                }
            )

        return {
            "generated_at": str(now),
            "overview": {
                "total_tasks": total_tasks,
                "total_users": total_users,
                "total_categories": total_categories,
            },
            "tasks_by_status": {
                "pending": status_counts.get("pending", 0),
                "in_progress": status_counts.get("in_progress", 0),
                "done": status_counts.get("done", 0),
                "cancelled": status_counts.get("cancelled", 0),
            },
            "tasks_by_priority": {
                "critical": priority_counts.get(1, 0),
                "high": priority_counts.get(2, 0),
                "medium": priority_counts.get(3, 0),
                "low": priority_counts.get(4, 0),
                "minimal": priority_counts.get(5, 0),
            },
            "overdue": {"count": len(overdue_list), "tasks": overdue_list},
            "recent_activity": {
                "tasks_created_last_7_days": recent_tasks,
                "tasks_completed_last_7_days": recent_done,
            },
            "user_productivity": user_stats,
        }

    def user_report(self, user):
        tasks = db.session.query(Task).filter_by(user_id=user.id).all()
        counts = {"done": 0, "pending": 0, "in_progress": 0, "cancelled": 0}
        overdue = 0
        high_priority = 0
        for t in tasks:
            if t.status in counts:
                counts[t.status] += 1
            if t.priority <= 2:
                high_priority += 1
            if is_overdue(t.due_date, t.status):
                overdue += 1

        total = len(tasks)
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": {
                "total_tasks": total,
                "done": counts["done"],
                "pending": counts["pending"],
                "in_progress": counts["in_progress"],
                "cancelled": counts["cancelled"],
                "overdue": overdue,
                "high_priority": high_priority,
                "completion_rate": round((counts["done"] / total) * 100, 2) if total else 0,
            },
        }
