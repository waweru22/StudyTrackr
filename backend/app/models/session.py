from app import db
from datetime import datetime

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    session_goal = db.Column(db.String(200))
    vibe = db.Column(db.String(50)) # Low Energy, High Energy
    social_setting = db.Column(db.String(50)) # Solo, Group
    learning_mode = db.Column(db.String(50)) # Active Recall, Deep Work
    medium = db.Column(db.String(50)) # Digital, Paper
    environment = db.Column(db.String(50)) # Library, Home
    
    environment = db.Column(db.String(50)) # Library, Home
    
    distraction_count = db.Column(db.Integer, default=0) # Max 2
    # pause_duration field deprecated in favor of total_distraction_seconds calculation at runtime
    duration_minutes = db.Column(db.Integer, default=0)
    success_score = db.Column(db.Float, default=0.0)
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # Post-session feedback fields
    mood_after = db.Column(db.Integer, nullable=True)  # 1=Drained, 2=Neutral, 3=Energized
    actual_duration_minutes = db.Column(db.Integer, nullable=True)
    completed_on_time = db.Column(db.Boolean, nullable=True)
    would_repeat = db.Column(db.Boolean, nullable=True)
    session_insight = db.Column(db.String(500), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    course = db.relationship('Course', backref=db.backref('sessions', lazy=True))

class ScheduleBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True) # Can be null for generic blocks?
    
    day_of_week = db.Column(db.String(10), nullable=False) # Monday, Tuesday
    date = db.Column(db.Date, nullable=True) # For specific calendar days
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    block_type = db.Column(db.String(50)) # Deep Work, Active Recall, Break
    
    # New Fields for Expert System
    status = db.Column(db.String(20), default='upcoming', nullable=False) # upcoming, completed, missed
    technique_name = db.Column(db.String(100), nullable=True, default='')
    technique_details = db.Column(db.Text, nullable=True, default='')

    # Suggested study conditions (from user onboarding data)
    suggested_environment = db.Column(db.String(100), nullable=True)
    suggested_social_setting = db.Column(db.String(50), nullable=True)
    suggested_medium = db.Column(db.String(50), nullable=True)

    
    # Rule Engine Metadata (Transparency)
    refinement_reason = db.Column(db.String(100)) # The principle applied
    academic_citation = db.Column(db.String(100)) # e.g. "Bjork & Bjork (2011)"
    logic_explanation = db.Column(db.String(255)) # Why this decision was made
    
    user = db.relationship('User', backref=db.backref('schedule_blocks', lazy=True))
    course = db.relationship('Course', backref=db.backref('scheduled_events', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_session_match(self, session_datetime):
        """
        Validation: Checks if a session timestamp matches this block's date/time window.
        """
        if not self.date:
            return False
            
        # Combine block date+time
        block_dt_start = datetime.combine(self.date, self.start_time)
        block_dt_end = datetime.combine(self.date, self.end_time)
        
        # Check if session start is within [Start, End]
        # Or reasonably close (e.g. +/- 15 mins)? 
        # Requirement says "correctly handles the comparison", strict matching usually implies window check.
        # "attended a specific scheduled block" -> Session Start >= Block Start & Session Start < Block End
        return block_dt_start <= session_datetime < block_dt_end
