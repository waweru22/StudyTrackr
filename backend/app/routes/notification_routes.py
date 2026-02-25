from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService

notification_bp = Blueprint("notifications", __name__)

@notification_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    notifications = NotificationService.get_user_notifications(user_id)
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in notifications])

@notification_bp.route("/<int:notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_notification_as_read(notification_id):
    user_id = int(get_jwt_identity())
    notification = NotificationService.mark_as_read(notification_id, user_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify({"message": "Marked as read"})

@notification_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_as_read():
    user_id = int(get_jwt_identity())
    NotificationService.mark_all_as_read(user_id)
    return jsonify({"message": "All notifications marked as read"})
