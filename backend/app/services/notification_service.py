from app import db
from app.models.notification import Notification

class NotificationService:

    @staticmethod
    def create_notification(user_id, title, message, type="system"):
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            print(f"[NotificationService] Failed to create notification: {e}")
            return None

    @staticmethod
    def get_user_notifications(user_id):
        return (
            Notification.query
            .filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification

    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({"is_read": True})
        db.session.commit()
