from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService
from app.services.fcm_service import FCMService

notification_bp = Blueprint("notifications", __name__)


# ── Notification Endpoints ────────────────────────────────────────────

@notification_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)

    notifications = NotificationService.get_user_notifications(
        user_id, limit=limit, unread_only=unread_only
    )
    return jsonify([n.to_dict() for n in notifications])


@notification_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    user_id = int(get_jwt_identity())
    count = NotificationService.get_unread_count(user_id)
    return jsonify({"unread_count": count})


@notification_bp.route("/<int:notification_id>/read", methods=["PUT", "POST"])
@jwt_required()
def mark_notification_as_read(notification_id):
    user_id = int(get_jwt_identity())
    success = NotificationService.mark_as_read(notification_id, user_id)
    if not success:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify({"message": "Marked as read"})


@notification_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_as_read():
    user_id = int(get_jwt_identity())
    NotificationService.mark_all_as_read(user_id)
    return jsonify({"message": "All notifications marked as read"})


@notification_bp.route("/<int:notification_id>/dismiss", methods=["POST"])
@jwt_required()
def dismiss_notification(notification_id):
    user_id = int(get_jwt_identity())
    success = NotificationService.dismiss_notification(notification_id, user_id)
    if not success:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify({"message": "Notification dismissed"})


@notification_bp.route("/clear", methods=["POST"])
@jwt_required()
def clear_all():
    user_id = int(get_jwt_identity())
    count = NotificationService.clear_all_notifications(user_id)
    return jsonify({"message": f"Cleared {count} notifications", "count": count})


# ── FCM Token Endpoints ──────────────────────────────────────────────

@notification_bp.route("/fcm/register-token", methods=["POST"])
@jwt_required()
def register_fcm_token():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    token = data.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    device_type = data.get('device_type', 'web')
    browser_name = data.get('browser_name')

    result = FCMService.register_device_token(user_id, token, device_type, browser_name)
    if result:
        return jsonify({"message": "FCM token registered", "token_id": result.id})
    return jsonify({"error": "Failed to register token"}), 500


@notification_bp.route("/fcm/unregister-token", methods=["POST"])
@jwt_required()
def unregister_fcm_token():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    token = data.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    success = FCMService.unregister_device_token(user_id, token)
    if success:
        return jsonify({"message": "FCM token unregistered"})
    return jsonify({"error": "Token not found"}), 404


@notification_bp.route("/fcm/tokens", methods=["GET"])
@jwt_required()
def get_fcm_tokens():
    user_id = int(get_jwt_identity())
    tokens = FCMService.get_user_tokens(user_id)
    return jsonify([t.to_dict() for t in tokens])
