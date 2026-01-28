from app import db

class UserCourse(db.Model):
    __tablename__ = 'user_courses'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Relationships
    # user backref defined in User model or here? Usually here for association object pattern or simpler.
    # Let's stick to definition here if possible, but simpler:
    
    # Let's just define table columns here. User model will define relationship.

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False) # 1-5
    # Remove is_favorite from global course
    # is_favorite = db.Column(db.Boolean, default=False) 
    
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
