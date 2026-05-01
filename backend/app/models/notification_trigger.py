from app import db
from datetime import datetime


class NotificationTrigger(db.Model):
    __tablename__ = 'notification_trigger'

    id = db.Column(db.Integer, primary_key=True)
    trigger_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.String(10), default='low')  # low, medium, urgent
    notification_type = db.Column(db.String(20), default='system')  # achievement, warning, tip, insight, admin_broadcast
    email_on_delivery = db.Column(db.Boolean, default=False)
    send_push = db.Column(db.Boolean, default=True)
    template_title = db.Column(db.String(200), nullable=False)
    template_message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def render(self, context_data=None):
        """Render template_title and template_message with context_data dict."""
        ctx = context_data or {}
        try:
            title = self.template_title.format(**ctx)
        except (KeyError, IndexError):
            title = self.template_title
        try:
            message = self.template_message.format(**ctx)
        except (KeyError, IndexError):
            message = self.template_message
        return title, message

    def to_dict(self):
        return {
            'id': self.id,
            'trigger_name': self.trigger_name,
            'description': self.description,
            'is_active': self.is_active,
            'priority': self.priority,
            'notification_type': self.notification_type,
            'send_push': self.send_push,
            'template_title': self.template_title,
            'template_message': self.template_message,
        }
