"""
Firebase Cloud Messaging Service.
Handles push notification delivery and FCM token management.
All methods are fail-safe — FCM errors never crash the application.
"""
import os
from datetime import datetime
from app import db
from app.models.fcm_token import FCMToken
from app.models.notification import Notification

# Firebase Admin SDK (lazy-imported to avoid crash if not installed)
_firebase_initialized = False


class FCMService:

    @staticmethod
    def initialize_firebase():
        """Initialize Firebase Admin SDK from environment variables.
        Called once on app startup. Logs warning if credentials are missing."""
        global _firebase_initialized

        try:
            import firebase_admin
            from firebase_admin import credentials

            # Skip if already initialized
            if firebase_admin._apps:
                _firebase_initialized = True
                print("[FCM] Firebase already initialized.")
                return True

            project_id = os.getenv('FIREBASE_PROJECT_ID')
            private_key = os.getenv('FIREBASE_PRIVATE_KEY')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')

            if not all([project_id, private_key, client_email]):
                print("[FCM] WARNING: Firebase credentials missing. Push notifications disabled.")
                return False

            # Handle escaped newlines in private key
            if private_key:
                private_key = private_key.replace('\\n', '\n')

            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            })
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            print(f"[FCM] Firebase initialized for project: {project_id}")
            return True

        except Exception as e:
            print(f"[FCM] WARNING: Firebase initialization failed: {e}")
            _firebase_initialized = False
            return False

    @staticmethod
    def send_push_notification_sync(notification_id):
        """Send push notification to all active FCM tokens for the notification's user.
        This is called from a background thread — must create its own app context."""
        global _firebase_initialized

        if not _firebase_initialized:
            return False

        try:
            from flask import current_app
            # We need app context in the background thread
            from app import create_app
            app = create_app()

            with app.app_context():
                notification = Notification.query.get(notification_id)
                if not notification:
                    print(f"[FCM] Notification {notification_id} not found.")
                    return False

                tokens = FCMToken.query.filter_by(
                    user_id=notification.user_id,
                    is_active=True
                ).all()

                if not tokens:
                    return False

                sent_count = 0
                for token_record in tokens:
                    success = FCMService._send_to_device(token_record, notification)
                    if success:
                        sent_count += 1

                if sent_count > 0:
                    notification.push_sent = True
                    notification.push_sent_at = datetime.utcnow()
                    db.session.commit()
                    print(f"[FCM] Sent push for notification {notification_id} to {sent_count} device(s).")

                return sent_count > 0

        except Exception as e:
            print(f"[FCM_ERROR] Failed to send push for notification {notification_id}: {e}")
            return False

    @staticmethod
    def _send_to_device(fcm_token_record, notification):
        """Send a single FCM message to one device token."""
        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.message,
                ),
                data={
                    'notification_id': str(notification.id),
                    'action_url': notification.action_url or '/dashboard',
                    'type': notification.type or 'system',
                },
                token=fcm_token_record.token,
            )

            response = messaging.send(message)
            # Update last_used_at
            fcm_token_record.last_used_at = datetime.utcnow()
            db.session.commit()
            return True

        except Exception as e:
            error_str = str(e).lower()
            # Mark token inactive if it's invalid/expired
            if any(keyword in error_str for keyword in ['invalid', 'not-registered', 'unregistered', '401', '403']):
                FCMService.mark_token_inactive(fcm_token_record.id)
                print(f"[FCM] Marked token {fcm_token_record.id} inactive (invalid).")
            else:
                print(f"[FCM_ERROR] Failed to send to device: {e}")
            return False

    @staticmethod
    def mark_token_inactive(fcm_token_id):
        """Soft-deactivate an FCM token (don't delete — keep for audit)."""
        try:
            token = FCMToken.query.get(fcm_token_id)
            if token:
                token.is_active = False
                db.session.commit()
        except Exception as e:
            print(f"[FCM_ERROR] Failed to mark token inactive: {e}")

    # ── Token Management ──────────────────────────────────────────────

    @staticmethod
    def register_device_token(user_id, token, device_type='web', browser_name=None):
        """Register or re-activate an FCM token for a user."""
        try:
            existing = FCMToken.query.filter_by(token=token).first()
            if existing:
                # Reactivate and update
                existing.is_active = True
                existing.user_id = user_id
                existing.device_type = device_type
                existing.browser_name = browser_name
                existing.last_used_at = datetime.utcnow()
                db.session.commit()
                print(f"[FCM_REGISTER] Reactivated token for user {user_id}")
                return existing

            new_token = FCMToken(
                user_id=user_id,
                token=token,
                device_type=device_type,
                browser_name=browser_name,
                is_active=True,
                last_used_at=datetime.utcnow(),
            )
            db.session.add(new_token)
            db.session.commit()
            print(f"[FCM_REGISTER] Registered new token for user {user_id}")
            return new_token

        except Exception as e:
            db.session.rollback()
            print(f"[FCM_ERROR] Failed to register token: {e}")
            return None

    @staticmethod
    def unregister_device_token(user_id, token):
        """Soft-deactivate a specific token for a user."""
        try:
            record = FCMToken.query.filter_by(user_id=user_id, token=token).first()
            if record:
                record.is_active = False
                db.session.commit()
                print(f"[FCM_UNREGISTER] Unregistered token for user {user_id}")
                return True
            return False
        except Exception as e:
            print(f"[FCM_ERROR] Failed to unregister token: {e}")
            return False

    @staticmethod
    def get_user_tokens(user_id):
        """Return all active tokens for a user."""
        return FCMToken.query.filter_by(user_id=user_id, is_active=True).all()
