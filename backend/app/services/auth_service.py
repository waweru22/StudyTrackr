import random
import string
from datetime import datetime, timedelta
from app import db
from app.models.user import EmailVerification, User
from werkzeug.security import generate_password_hash, check_password_hash

from app.services.mail_service import MailService

class AuthService:
    @staticmethod
    def generate_otp(email):
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=5) # 5 minutes per req
        
        # Save to DB
        verification = EmailVerification(
            email=email,
            otp_code=otp,
            expires_at=expires_at
        )
        db.session.add(verification)
        db.session.commit()
        
        # Send Email via Service
        MailService.send_otp_email(email, otp)
        
        return otp

    @staticmethod
    def verify_otp(email, code):
        email = email.strip().lower() # Sanitize
        
        verification = EmailVerification.query.filter_by(
            email=email, 
            otp_code=code, 
            is_used=False
        ).order_by(EmailVerification.expires_at.desc()).first()
        
        if not verification:
            return False, "Invalid OTP"
            
        if verification.expires_at < datetime.utcnow():
            return False, "OTP Expired"
            
        # Mark as used
        verification.is_used = True
        db.session.commit()
        
        # Hard Fix: Force session reload to ensure subsequent queries see fresh data
        db.session.expire_all()
        
        return True, "Verified"

    @staticmethod
    def register_user(data, commit=True):
        # Fix: Initialize variables at the start
        new_user = None
        msg = "Registration successful. Please verify your email."
        warnings = []

        try:
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            # Validation Logic
            if not password or not confirm_password:
                return None, "Password and confirm_password are required"
            if password != confirm_password:
                return None, "Passwords do not match."
            if len(password) < 8:
                return None, "Password must be at least 8 characters long."

            # Sanitization
            email = data.get('email', '').strip().lower()
            if not email:
                return None, "Email is required"

            # Unique Email Constraint
            if User.query.filter_by(email=email).first():
                return None, "User already exists"
                
            # Course Limit Validation
            selected_codes = data.get('selected_course_codes', [])
            if len(selected_codes) > 12:
                return None, "Course limit exceeded. You can select up to 12 courses."
                
            role = data.get('role', 'student')
            staff_id = data.get('staff_id')
                
            new_user = User(
                username=data.get('username'),
                email=email,
                hashed_password=generate_password_hash(password),
                level=data.get('level', 100),
                role=role,
                staff_id=staff_id,
                learning_style=data.get('learning_style', 'Unknown'),
                peak_time=data.get('peak_time'),
                base_template=data.get('base_template'),
                environment_pref=data.get('environment_pref'),
                focus_threshold=data.get('focus_threshold', 60),
                preferred_environment_v2=data.get('preferred_environment'),
                study_mode=data.get('study_mode')
            )
            
            # Add Courses with Level Mismatch Validation
            from app.models.course import Course
            selected_ids = data.get('selected_course_ids', [])
            
            if selected_ids:
                courses_to_add = Course.query.filter(Course.id.in_(selected_ids)).all()
                user_level = data.get('level')
                for c in courses_to_add:
                    if c.level != user_level:
                        warnings.append(f"{c.code} (Lvl {c.level}) added as elective.")
                
                if not courses_to_add:
                     warnings.append("No valid courses found from selection.")
                else:
                     new_user.courses.extend(courses_to_add)
                
            db.session.add(new_user)
            if commit:
                db.session.commit()
            else:
                db.session.flush() # Ensure ID is generated for caller
            
            # Append warnings to the msg
            if warnings:
                msg += " [Warnings: " + "; ".join(warnings) + "]"
                
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"
            
        return new_user, msg

    @staticmethod
    def login_user(email, password):
        if not email or not password:
            return None, "Email and password are required"
            
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.hashed_password, password):
            return user, "Login successful"
            
        return None, "Invalid email or password"
