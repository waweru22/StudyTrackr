from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.inference_service import InferenceService
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db # Need to get user to create token
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    
    user, message = AuthService.login_user(email, password)
    
    if user:
        token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": message,
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "level": user.level,
                "role": user.role
            }
        }), 200
        
    return jsonify({"error": message}), 401

@auth_bp.route('/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    otp = AuthService.generate_otp(email)
    # Security: Do not return OTP in response
    return jsonify({"message": "OTP sent to email"}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    db.session.commit() # Ensure fresh view
    data = request.get_json()
    email = data.get('email', '').strip()
    code = data.get('otp_code')
    
    success, message = AuthService.verify_otp(email, code)
    if not success:
        return jsonify({"error": message}), 400
        
    # Check if user exists to token
    user = User.query.filter_by(email=email).first()
    token = None
    user_id = None
    if user:
        token = create_access_token(identity=str(user.id))
        user_id = user.id
        
    return jsonify({
        "message": message, 
        "access_token": token,
        "user_id": user_id
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
    
    try:
        # 1. Register User (No Commit yet)
        user, message = AuthService.register_user(data, commit=False)
        if not user:
            return jsonify({"error": message}), 400
        
        # 2. Get Course IDs for Inference
        # User.courses are available in session (flushed)
        course_ids = [c.id for c in user.courses]
        
        # 3. Trigger Inference Engine
        # Pass IDs explicitly as requested
        sched_result = InferenceService.generate_week_schedule(user.id, selected_course_ids=course_ids)
        if sched_result and "No courses" in sched_result:
             db.session.rollback()
             return jsonify({"error": sched_result}), 400

        # 4. Trigger OTP Email
        AuthService.generate_otp(user.email)
        
        # 5. ATOMIC COMMIT
        db.session.commit()
        
        return jsonify({"message": message, "user_id": user.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Onboarding Failed: {str(e)}")
        return jsonify({"error": "Registration failed due to system error."}), 500
