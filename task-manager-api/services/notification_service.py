"""Serviço de notificação — credenciais SMTP vêm do ambiente (não hardcoded)."""
import logging
import os
import smtplib

from utils.helpers import now_utc

logger = logging.getLogger("notifications")


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.email_port = int(os.environ.get("SMTP_PORT", "587"))
        self.email_user = os.environ.get("SMTP_USER", "")
        self.email_password = os.environ.get("SMTP_PASSWORD", "")

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            logger.info("SMTP não configurado; e-mail para %s não enviado", to)
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info("e-mail enviado para %s", to)
            return True
        except Exception:
            logger.exception("falha ao enviar e-mail para %s", to)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {
                "type": "task_assigned",
                "user_id": user.id,
                "task_id": task.id,
                "timestamp": now_utc(),
            }
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n["user_id"] == user_id]
