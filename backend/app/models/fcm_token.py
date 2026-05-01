from app import db
from datetime import datetime


class FCMToken(db.Model):
    __tablename__ = 'fcm_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    device_type = db.Column(db.String(20), default='web')  # web, mobile
    browser_name = db.Column(db.String(50), nullable=True)  # Chrome, Firefox, Safari
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('fcm_tokens', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'device_type': self.device_type,
            'browser_name': self.browser_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
        }
