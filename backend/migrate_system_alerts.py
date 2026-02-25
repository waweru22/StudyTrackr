"""
One-time migration: copies existing SystemAlert records into the Notification table.
Safe to re-run — skips duplicates based on user_id + message + created_at.
"""
from app import create_app, db
from app.models.system_alert import SystemAlert
from app.models.notification import Notification
from datetime import datetime

app = create_app()
with app.app_context():
    alerts = SystemAlert.query.all()
    migrated = 0
    for alert in alerts:
        # SystemAlert has no title field — derive from message
        title = "Missed session" if "missed" in (alert.message or "").lower() else "System Alert"

        # Avoid duplicates if script is run more than once
        exists = Notification.query.filter_by(
            user_id=alert.user_id,
            message=alert.message,
            created_at=alert.created_at
        ).first()
        if not exists:
            n = Notification(
                user_id=alert.user_id,
                title=title,
                message=alert.message or "",
                type="alert",
                is_read=alert.is_read or False,
                created_at=alert.created_at or datetime.utcnow()
            )
            db.session.add(n)
            migrated += 1
    db.session.commit()
    print(f"Migrated {migrated} SystemAlert records into Notification table.")
