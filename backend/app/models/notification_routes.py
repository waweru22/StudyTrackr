from flask import Blueprint, jsonify, request
from app.services.notification_service import NotificationService
from app.models.notification import Notification

notification_bp = Blueprint("notifications", __name__)

@notification_bp.route("/", methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter required"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    notifications = NotificationService.get_user_notifications(user_id)
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "is_read": n.is_read,
        "created_at": n.created_at
    } for n in notifications])

@notification_bp.route("/<int:notification_id>/read", methods=["PUT"])
def mark_notification_as_read(notification_id):
    notification = NotificationService.mark_as_read(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify({"message": "Notification marked as read"})
