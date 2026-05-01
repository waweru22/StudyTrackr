from app import db
from datetime import datetime


class PendingRegistration(db.Model):
    """Temporary storage for registration data before OTP verification.
    The user is NOT created until OTP is successfully verified."""
    __tablename__ = 'pending_registration'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_data = db.Column(db.Text, nullable=False)  # JSON blob
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
