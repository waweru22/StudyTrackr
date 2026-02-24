from app import db
from app.models.notification import Notification
from app.services.mail_service import send_email, MailService

class NotificationService:

    @staticmethod
    def create_notification(user_id, title, message, type="system", send_email_flag=False, user_email=None):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        db.session.add(notification)
        db.session.commit()

        if send_email_flag and user_email:
            # use the helper function; MailService is available for more complex flows
            try:
                send_email(
                    to=user_email,
                    subject=title,
                    body=message
                )
            except Exception as e:
                # shouldn't crash entire request, just log
                from app import app as _app
                _app.logger.exception(f"failed sending notification email to {user_email}")

        return notification

    @staticmethod
    def get_user_notifications(user_id):
        return Notification.query.filter_by(user_id=user_id)            .order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification
