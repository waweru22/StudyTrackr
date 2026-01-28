import random
import string
from datetime import datetime, timedelta
from app import db
from app.models.user import EmailVerification, User
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    @staticmethod
    def generate_otp(email):
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Save to DB
        verification = EmailVerification(
            email=email,
            otp_code=otp,
            expires_at=expires_at
        )
        db.session.add(verification)
        db.session.commit()
        
        # Log to console as requested
        print(f"[{datetime.utcnow()}] OTP for {email}: {otp}")
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
    def register_user(data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Validation Logic
        if not password or not confirm_password:
            return None, "Password and confirm_password are required"
            
        if password != confirm_password:
            return None, "Passwords do not match."
            
        if len(password) < 8:
            return None, "Password must be at least 8 characters long."

        if len(password) < 8:
            return None, "Password must be at least 8 characters long."

        # Sanitize Email
        email = data.get('email', '').strip().lower()
        if not email:
            return None, "Email is required"

        if User.query.filter_by(email=email).first():
            return None, "User already exists"
            
        # Validate Course Limit (Max 12)
        selected_ids = data.get('selected_course_ids', [])
        if len(selected_ids) > 12:
            return None, "Course limit exceeded. You can select up to 12 courses."

        # Hash Password
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"
            
        role = data.get('role', 'student')
        staff_id = data.get('staff_id')
            
        new_user = User(
            username=data.get('username'),
            email=email,
            hashed_password=generate_password_hash(password),
            level=data.get('level', 100),
            role=role,
            staff_id=staff_id,
            # Defaults for inference fields
            learning_style=data.get('learning_style', 'Unknown'),
            # ... other fields default to model defaults or None
            peak_time=data.get('peak_time'),
            base_template=data.get('base_template'),
            environment_pref=data.get('environment_pref'),
            
            # New Advanced Profiling
            focus_threshold=data.get('focus_threshold', 60),
            preferred_environment_v2=data.get('preferred_environment'),
            study_mode=data.get('study_mode')
        )
        
        # Add Courses
        from app.models.course import Course
        warnings = []
        if selected_ids:
            courses_to_add = Course.query.filter(Course.id.in_(selected_ids)).all()
            
            # Level Mismatch Validation
            user_level = data.get('level')
            for c in courses_to_add:
                # "If a Level 400 user tries to add a Level 100 course, return a warning"
                # Doing strict check or just warning? 
                # Prompt: "return a warning or allow it only as an elective."
                # Let's simple check strict equality or range?
                # Usually users take courses at their level.
                if c.level != user_level:
                    warnings.append(f"Course {c.code} (Level {c.level}) does not match your level ({user_level}). Added as elective.")
            
            new_user.courses.extend(courses_to_add)
            
        db.session.add(new_user)
        db.session.commit()
        
        msg = "Success"
        if warnings:
            msg += " [Warnings: " + "; ".join(warnings) + "]"
            
        return new_user, msg
