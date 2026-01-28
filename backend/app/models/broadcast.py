from app import db
from datetime import datetime

class Broadcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    target_level = db.Column(db.Integer, nullable=False) # e.g. 100, 200, 0 for All
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to fetch admin details if needed
    admin = db.relationship('User', backref=db.backref('broadcasts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'message': self.message,
            'target_level': self.target_level,
            'timestamp': self.timestamp.isoformat()
        }
