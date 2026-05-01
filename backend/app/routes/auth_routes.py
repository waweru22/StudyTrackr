from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.inference_service import InferenceService
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db # Need to get user to create token
from werkzeug.security import check_password_hash
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    if not identifier:
         # Fallback for legacy frontend that might still send 'email'
         identifier = data.get('email', '').strip().lower()
         
    password = data.get('password')
    
    user, message = AuthService.login_user(identifier, password)
    
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
@auth_bp.route('/resend-otp', methods=['POST'])
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
    
    # ── After OTP is verified, check for pending registration ──
    from app.models.pending_registration import PendingRegistration
    pending = PendingRegistration.query.filter_by(email=email.lower()).first()
    
    if pending:
        # This is a new registration — create the user now
        try:
            reg_data = json.loads(pending.registration_data)
            
            # 1. Create User
            user, reg_message = AuthService.register_user(reg_data, commit=False)
            if not user:
                return jsonify({"error": reg_message}), 400
            
            # 2. Generate schedule
            course_ids = [c.id for c in user.courses]
            sched_result = InferenceService.generate_week_schedule(user.id, selected_course_ids=course_ids)
            if sched_result and "No courses" in sched_result:
                print(f"Warning: {sched_result}")
            
            # 3. Commit user + schedule atomically
            db.session.commit()
            
            # 4. Clean up pending registration
            PendingRegistration.query.filter_by(email=email.lower()).delete()
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            return jsonify({
                "message": "Email verified. Account created successfully.",
                "access_token": token,
                "user_id": user.id
            }), 200
            
        except Exception as e:
            db.session.rollback()
            print(f"[verify-otp] Registration failed after OTP: {e}")
            return jsonify({"error": "Registration failed after verification. Please try again."}), 500
    
    # ── Existing user verifying OTP (e.g. password reset, re-verification) ──
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
    import os
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    staff_id = data.get('staff_id')
    admin_key = data.get('admin_key')
    
    # 1. Verify SECRET_ADMIN_KEY
    expected_key = os.getenv('SECRET_ADMIN_KEY')
    if not admin_key or admin_key != expected_key:
        print(f"[SECURITY] Failed admin registration attempt for email={email}")
        return jsonify({"error": "Invalid admin key"}), 401
    
    # 2. Validate email domain
    if not email or not email.endswith('@nileuni.edu.ng'):
        return jsonify({"error": "Invalid email domain. Must be @nileuni.edu.ng"}), 400
        
    if not staff_id:
        return jsonify({"error": "Staff ID is required"}), 400
    
    # 3. Register admin user (no courses, no onboarding)
    data['role'] = 'admin'
    data['email'] = email
    data['level'] = data.get('level', 0)
    data['username'] = data.get('username') or staff_id  # Use staff_id as username fallback
    
    user, message = AuthService.register_user(data)
    
    if not user:
        return jsonify({"error": message}), 400
    
    # 4. Set admin as auto-verified
    user.is_verified = True
    db.session.commit()
    
    # 5. Generate token directly (no OTP needed for admin)
    token = create_access_token(identity=str(user.id))
    
    return jsonify({
        "message": "Admin registered successfully.",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "staff_id": user.staff_id
        }
    }), 201

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.hashed_password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if user.role != 'admin':
        return jsonify({"error": "Access denied. Admin accounts only."}), 403
    
    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Admin login successful",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "staff_id": user.staff_id
        }
    }), 200

@auth_bp.route('/onboard', methods=['POST'])
def onboard():
    """Step 1: Validate data, send OTP, store data in PendingRegistration.
    The User is NOT created here — only after OTP verification."""
    data = request.get_json()
    
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # ── Validate before doing anything ──
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not password or not confirm_password:
            return jsonify({"error": "Password and confirm_password are required"}), 400
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match."}), 400
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long."}), 400
        
        # Check if email already registered as a real user
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "User already exists"}), 400
        
        # Course limit check
        selected_codes = data.get('selected_course_codes', [])
        if len(selected_codes) > 12:
            return jsonify({"error": "Course limit exceeded. You can select up to 12 courses."}), 400
        
        # ── Store registration data for later (after OTP) ──
        from app.models.pending_registration import PendingRegistration
        
        # Upsert: remove old pending for this email if exists
        PendingRegistration.query.filter_by(email=email).delete()
        
        pending = PendingRegistration(
            email=email,
            registration_data=json.dumps(data)
        )
        db.session.add(pending)
        db.session.commit()
        
        # ── Send OTP ──
        AuthService.generate_otp(email)
        
        return jsonify({"message": "OTP sent to your email. Please verify to complete registration."}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Onboarding Failed: {str(e)}")
        return jsonify({"error": "Registration failed due to system error."}), 500
