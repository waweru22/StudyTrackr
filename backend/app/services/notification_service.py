from app import db
from app.models.notification import Notification
from app.models.notification_trigger import NotificationTrigger
from datetime import datetime


class NotificationService:
    """
    Unified notification service.
    - Trigger-based: create_triggered_notification(user_id, trigger_name, context_data)
    - Direct: create_notification(user_id, title, message, type) for admin broadcasts / legacy
    """

    # ── Trigger-based creation (Phase 2) ──────────────────────────────

    @staticmethod
    def create_triggered_notification(user_id, trigger_name, context_data=None, skip_push=False):
        """Create a notification from a registered trigger.
        Returns the Notification object, or None if the trigger is inactive/missing."""
        try:
            trigger = NotificationTrigger.query.filter_by(trigger_name=trigger_name).first()
            if not trigger:
                print(f"[NOTIFICATION] Trigger '{trigger_name}' not found. Skipping.")
                return None

            if not trigger.is_active:
                return None

            # Render template with context
            title, message = trigger.render(context_data)

            # Determine action_url from context or trigger type defaults
            action_url_map = {
                'badge_earned': '/profile',
                'burnout_warning': '/profile',
                'streak_milestone': '/dashboard',
                'low_efficacy_session': '/schedule',
                'missed_session': '/schedule',
                'course_struggling': '/materials',
                'peak_time_reminder': '/schedule',
                'weekly_insights': '/dashboard',
                'schedule_adapted': '/schedule',
                'long_gap_alert': '/dashboard',
            }
            action_url = action_url_map.get(trigger_name, '/dashboard')

            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=trigger.notification_type,
                trigger_id=trigger.id,
                action_url=action_url,
                is_read=False,
                push_sent=False,
            )
            db.session.add(notification)
            db.session.commit()

            print(f"[NOTIFICATION] Created '{trigger_name}' for user {user_id}")

            # Async push via FCM (non-blocking)
            if trigger.send_push and not skip_push:
                try:
                    from app.services.fcm_service import FCMService
                    from app.utils.background_tasks import create_task
                    create_task(FCMService.send_push_notification_sync, notification.id)
                except Exception as e:
                    print(f"[NOTIFICATION] FCM push scheduling failed (non-fatal): {e}")

            return notification

        except Exception as e:
            db.session.rollback()
            print(f"[NOTIFICATION] Failed to create triggered notification: {e}")
            return None

    # ── Direct creation (legacy / admin broadcasts) ───────────────────

    @staticmethod
    def create_notification(user_id, title, message, type="system", action_url=None):
        """Create a notification directly (no trigger). Backward-compatible."""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                action_url=action_url,
                is_read=False,
                push_sent=False,
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            print(f"[NOTIFICATION] Failed to create notification: {e}")
            return None

    # ── Read / Dismiss / Query ────────────────────────────────────────

    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def dismiss_notification(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.dismissed_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_notifications(user_id, limit=50, unread_only=False, include_dismissed=False):
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        if not include_dismissed:
            query = query.filter(Notification.dismissed_at.is_(None))

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).filter(
            Notification.dismissed_at.is_(None)
        ).count()

    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({"is_read": True})
        db.session.commit()

    @staticmethod
    def clear_all_notifications(user_id):
        """Soft-dismiss all notifications for user."""
        now = datetime.utcnow()
        count = Notification.query.filter_by(user_id=user_id).filter(
            Notification.dismissed_at.is_(None)
        ).update({"dismissed_at": now})
        db.session.commit()
        return count
