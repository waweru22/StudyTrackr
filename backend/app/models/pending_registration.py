from app import db
from datetime import datetime


class PendingRegistration(db.Model):
    """Temporary storage for registration data before email verification.
    The user is NOT created until the verification link is clicked."""
    __tablename__ = 'pending_registration'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_data = db.Column(db.Text, nullable=False)  # JSON blob
    verification_token = db.Column(db.String(100), unique=True, nullable=False)
    token_expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
