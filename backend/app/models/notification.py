from app import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), default='system')  # system | encouragement | alert | milestone | achievement | warning | tip | insight | admin_broadcast

    # Trigger system (Phase 2)
    trigger_id = db.Column(db.Integer, db.ForeignKey('notification_trigger.id'), nullable=True)
    action_url = db.Column(db.String(200), nullable=True)  # e.g. '/schedule', '/profile'

    # Read / Dismiss state
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    dismissed_at = db.Column(db.DateTime, nullable=True)

    # FCM push tracking
    push_sent = db.Column(db.Boolean, default=False)
    push_sent_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    trigger = db.relationship('NotificationTrigger', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'push_sent': self.push_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
