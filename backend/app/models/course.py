from app import db
from datetime import datetime

class UserCourse(db.Model):
    __tablename__ = 'user_courses'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    is_favorite = db.Column(db.Boolean, default=False)
    
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False) # 1-5
    
    # Relationship to User via UserCourses
    students = db.relationship('User', secondary='user_courses', back_populates='courses')

class StudyKnowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    principle = db.Column(db.String(100), nullable=False)
    rule_logic = db.Column(db.String(200)) # Internal logic trigger
    content = db.Column(db.Text, nullable=False)
    inference_trigger = db.Column(db.String(50)) # e.g., 'forgetting_curve'
    academic_source = db.Column(db.String(100))
    tags = db.Column(db.String(100)) # Comma-separated tags
    rule_type = db.Column(db.String(20), default='schedule')  # 'schedule' or 'session'
    student_instruction = db.Column(db.Text, nullable=True)

class SavedResource(db.Model):
    __tablename__ = 'saved_resource'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # video, textbook
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: one user can't save the same URL twice
    __table_args__ = (
        db.UniqueConstraint('user_id', 'url', name='uq_user_resource_url'),
    )

    user = db.relationship('User', backref=db.backref('saved_resources', lazy=True))
