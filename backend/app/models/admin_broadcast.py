from app import db
from datetime import datetime

class AdminBroadcast(db.Model):
    __tablename__ = 'admin_broadcast'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    target_level = db.Column(db.Integer, nullable=True)  # NULL = all students
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(120), nullable=False)  # Admin email for audit

    admin = db.relationship('User', backref=db.backref('admin_broadcasts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'title': self.title,
            'message': self.message,
            'target_level': self.target_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
