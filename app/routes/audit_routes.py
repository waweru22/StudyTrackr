from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.audit_service import WeeklyAuditService

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/run', methods=['POST'])
@audit_bp.route('/run', methods=['POST'])
@jwt_required()
def trigger_audit():
    user_id = int(get_jwt_identity())
    result = WeeklyAuditService.perform_audit(user_id)
    return jsonify({"message": result}), 200
