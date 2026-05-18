from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    level = db.Column(db.Integer, nullable=False) # 100-400
    hashed_password = db.Column(db.String(200), nullable=False)
    
    # Access Control
    role = db.Column(db.String(20), default='student') # 'student', 'admin'
    staff_id = db.Column(db.String(50), nullable=True) # Only for admins
    is_verified = db.Column(db.Boolean, default=False) # Email verification status
    verification_token = db.Column(db.String(100), nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Inference Engine Profiles
    learning_style = db.Column(db.String(20)) # VARK
    peak_time = db.Column(db.String(20)) # Morning, Afternoon, Evening, Night
    base_template = db.Column(db.String(50)) # Balanced Sprinter, etc.
    zone_duration = db.Column(db.Integer, default=90) # Minutes
    environment_pref = db.Column(db.String(50))
    study_social_pref = db.Column(db.String(50))
    
    # New Profiling Fields (Advanced Logic)
    focus_threshold = db.Column(db.Integer, default=60) # Minutes (30, 60, 90)
    preferred_environment_v2 = db.Column(db.String(20)) # SILENT, AMBIENT, FLEXIBLE
    study_mode = db.Column(db.String(20)) # SOLO, GROUP
    daily_cognitive_budget = db.Column(db.Float, default=4.0) # Cognitive Load Budget (Sweller)
    
    # Gamification
    streak_count = db.Column(db.Integer, default=0)
    xp_points = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(50), default="Novice")
    
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', secondary='user_courses', back_populates='students')
    
    # Validation Logic for 12 courses limit should be checked in Service Layer
    # before appending to .courses list.

class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
