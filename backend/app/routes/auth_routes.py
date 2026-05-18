from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.inference_service import InferenceService
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db, limiter
from werkzeug.security import check_password_hash
import json
import secrets
import os
import re
from datetime import datetime, timedelta

# Compiled once, reused for all requests
STUDENT_EMAIL_PATTERN = re.compile(r'^\d{8,10}@nileuniversity\.edu\.ng$')

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    if not identifier:
         # Fallback for legacy frontend that might still send 'email'
         identifier = data.get('email', '').strip().lower()
         
    password = data.get('password')
    
    # Validate student email format (skip for username-based login)
    if '@' in identifier and not STUDENT_EMAIL_PATTERN.match(identifier.lower()):
        return jsonify({
            "error": "Invalid email format",
            "message": "Please use your Nile University student email (e.g. 20222208@nileuniversity.edu.ng)"
        }), 400
    
    user, message = AuthService.login_user(identifier, password)
    
    if user:
        # Check email verification status
        if not user.is_verified:
            return jsonify({
                "error": "Please verify your email before logging in.",
                "email_unverified": True
            }), 403

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
@limiter.limit("10 per minute")
def request_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    otp = AuthService.generate_otp(email)
    # Security: Do not return OTP in response
    return jsonify({"message": "OTP sent to email"}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
@limiter.limit("10 per minute")
def verify_otp():
    db.session.commit() # Ensure fresh view
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    code = data.get('otp_code')
    
    success, message = AuthService.verify_otp(email, code)
    if not success:
        return jsonify({"error": message}), 400
    
    # Existing user verifying OTP (e.g. password reset, re-verification)
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

@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    """Verifies a pending registration via the token and creates the real user."""
    from app.models.pending_registration import PendingRegistration
    from app.services.mail_service import MailService

    token = request.args.get('token')
    if not token:
        return jsonify({"error": "No token provided"}), 400
    
    pending = PendingRegistration.query.filter_by(verification_token=token).first()
    
    if not pending:
        return jsonify({"error": "Invalid verification link"}), 400
    
    if pending.token_expires_at < datetime.utcnow():
        return jsonify({"error": "Verification link has expired. Please register again."}), 400
    
    # Deserialise the stored registration data
    reg_data = json.loads(pending.registration_data)
    
    # Double-check no user was created in the meantime
    if User.query.filter_by(email=pending.email).first():
        db.session.delete(pending)
        db.session.commit()
        return jsonify({"error": "This email is already registered. Please log in."}), 400
    
    try:
        # 1. Create the real user now
        user, reg_message = AuthService.register_user(reg_data, commit=False)
        if not user:
            return jsonify({"error": reg_message}), 400
        
        user.is_verified = True
        user.verification_token = None
        user.token_expires_at = None
        
        # 2. Generate schedule
        course_ids = [c.id for c in user.courses]
        sched_result = InferenceService.generate_week_schedule(user.id, selected_course_ids=course_ids)
        if sched_result and "No courses" in str(sched_result):
            print(f"Warning: {sched_result}")
        
        # 3. Remove the pending registration
        db.session.delete(pending)
        db.session.commit()
        
        # 4. Return a JWT so the frontend can log them in immediately
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Email verified successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[verify-email] User creation failed: {e}")
        return jsonify({"error": "Verification failed due to a system error."}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
@limiter.limit("5 per minute")
def resend_verification():
    """Resend the verification email for a pending registration."""
    from app.models.pending_registration import PendingRegistration
    from app.services.mail_service import MailService

    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    pending = PendingRegistration.query.filter_by(email=email).first()
    
    if not pending:
        # Don't reveal whether email exists
        return jsonify({"message": "If that email is registered, a new verification link has been sent."}), 200
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    pending.verification_token = token
    pending.token_expires_at = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
    
    # Send verification email
    from flask import current_app
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
    verification_link = f"{frontend_url}/verify-email?token={token}"
    MailService.send_verification_email(email, verification_link)
    
    return jsonify({"message": "If that email is registered, a new verification link has been sent."}), 200

@auth_bp.route('/admin/register', methods=['POST'])
@limiter.limit("10 per minute")
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
    
    # 5. Generate token directly (no verification needed for admin)
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
@limiter.limit("10 per minute")
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
@limiter.limit("10 per minute")
def onboard():
    """Validate data, store in PendingRegistration, and send verification email.
    The real User is NOT created until the email link is clicked."""
    from app.models.pending_registration import PendingRegistration
    from app.services.mail_service import MailService

    data = request.get_json()
    
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        phone = data.get('phone', '').strip()
        
        # -- Validate before doing anything --
        if phone:
            import re
            NIGERIAN_PHONE = re.compile(r'^\+234[789][01]\d{8}$')
            if not NIGERIAN_PHONE.match(phone):
                return jsonify({
                    "error": "Invalid phone number",
                    "message": "Phone number must be a valid Nigerian number in +234 format"
                }), 400

        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not STUDENT_EMAIL_PATTERN.match(email):
            return jsonify({
                "error": "Invalid email format",
                "message": "Please use your Nile University student email (e.g. 20222208@nileuniversity.edu.ng)"
            }), 400
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
        selected_ids = data.get('selected_course_ids', [])
        if len(selected_ids) > 12:
            return jsonify({"error": "Course limit exceeded. You can select up to 12 courses."}), 400
            
        # Validate course_ids exist
        if selected_ids:
            from app.models.course import Course
            existing_courses = Course.query.filter(Course.id.in_(selected_ids)).count()
            if existing_courses != len(selected_ids):
                return jsonify({"error": "One or more selected courses are invalid or do not exist."}), 400
        
        # Generate verification token
        token = secrets.token_urlsafe(32)
        
        # Upsert PendingRegistration (replace if same email re-registers)
        existing_pending = PendingRegistration.query.filter_by(email=email).first()
        if existing_pending:
            existing_pending.registration_data = json.dumps(data)
            existing_pending.verification_token = token
            existing_pending.token_expires_at = datetime.utcnow() + timedelta(hours=24)
        else:
            pending = PendingRegistration(
                email=email,
                registration_data=json.dumps(data),
                verification_token=token,
                token_expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            db.session.add(pending)
        
        db.session.commit()
        
        # Send verification email
        from flask import current_app
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        verification_link = f"{frontend_url}/verify-email?token={token}"
        MailService.send_verification_email(email, verification_link)
        
        return jsonify({
            "message": "Please check your email to verify your account.",
            "email": email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Onboarding Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Registration failed due to system error."}), 500

