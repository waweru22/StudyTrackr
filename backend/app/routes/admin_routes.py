from flask import Blueprint, request, jsonify
from app.utils.decorators import admin_required
from app.services.admin_service import AdminService
from flask_jwt_extended import get_jwt_identity

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/analytics/focus', methods=['GET'])
@admin_required()
def get_focus_analytics():
    data = AdminService.get_low_focus_areas()
    return jsonify(data), 200

@admin_bp.route('/analytics/techniques', methods=['GET'])
@admin_required()
def get_technique_analytics():
    data = AdminService.get_technique_impact()
    return jsonify(data), 200

@admin_bp.route('/broadcast', methods=['POST'])
@admin_required()
def create_broadcast():
    data = request.get_json()
    admin_id = int(get_jwt_identity())
    message = data.get('message')
    target_level = data.get('target_level')
    
    if not message or not target_level:
        return jsonify({"error": "Message and target_level required"}), 400
        
    broadcast = AdminService.create_broadcast(admin_id, message, target_level)
    return jsonify({"message": "Broadcast Sent", "id": broadcast.id}), 201
