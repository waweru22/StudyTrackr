from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.inference_service import InferenceService
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db # Need to get user to create token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    otp = AuthService.generate_otp(email)
    return jsonify({"message": "OTP generated", "otp_debug": otp}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    db.session.commit() # Ensure fresh view
    data = request.get_json()
    email = data.get('email', '').strip()
    code = data.get('otp_code')
    
    success, message = AuthService.verify_otp(email, code)
    if not success:
        return jsonify({"error": message}), 400
        
    # Check if user exists to decide if login or signup flow, 
    # but requirement says verify-otp just validates. 
    # Realistically, it should issue a token if user exists.
    all_users = [u.email for u in User.query.all()]
    print(f"DEBUG DB Emails: {all_users}")
    print(f"DEBUG Looking for: '{email}'")
    user = User.query.filter_by(email=email).first()
    print(f"DEBUG Verify OTP: Email '{email}' Found User? {user}")
    token = None
    if user:
        token = create_access_token(identity=str(user.id))
        
    return jsonify({
        "message": message, 
        "access_token": token,
        "debug_user_found": str(user)
    }), 200

@auth_bp.route('/admin/register', methods=['POST'])
def register_admin():
    data = request.get_json()
    email = data.get('email')
    staff_id = data.get('staff_id')
    
    if not email or not email.endswith('@nileuni.edu.ng'):
        return jsonify({"error": "Invalid email domain. Must be @nileuni.edu.ng"}), 400
        
    if not staff_id:
        return jsonify({"error": "Staff ID is required"}), 400
        
    # Register user via Service (pass role='admin')
    # Use existing register_user but need to ensure it handles role/staff_id or update it
    # Actually, register_user in AuthService takes 'data' and creates User.
    # We should update AuthService.register_user to handle role/staff_id if present in data.
    
    # Inject role into data
    data['role'] = 'admin'
    
    user, message = AuthService.register_user(data)
    
    if not user:
        return jsonify({"error": message}), 400
        
    # Generate OTP for verification
    otp = AuthService.generate_otp(email)
    
    return jsonify({
        "message": "Admin Registration Successful. Please verify OTP.", 
        "otp_debug": otp, # Remove in prod
        "user_id": user.id
    }), 201

@auth_bp.route('/onboard', methods=['POST'])
def onboard():
    data = request.get_json()
    # Expects full profile data
    user, message = AuthService.register_user(data)
    if not user:
        return jsonify({"error": message}), 400
    
    # Trigger Inference Engine
    # Expects 'selected_courses': [id1, id2]
    course_ids = data.get('selected_course_ids', [])
    InferenceService.generate_week_schedule(user, course_ids)
    
    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Onboarding Complete", "access_token": token, "user_id": user.id}), 201
