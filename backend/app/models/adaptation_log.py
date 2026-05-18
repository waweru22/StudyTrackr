from datetime import datetime
from app import db


class AdaptationLog(db.Model):
    __tablename__ = "adaptation_log"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    week_label = db.Column(db.String(80))   # e.g. "Week 2 (19-25 May 2026)"
    summary    = db.Column(db.Text)         # one plain-English sentence
    reasoning  = db.Column(db.Text)         # JSON string

    user = db.relationship("User", backref="adaptation_logs")
