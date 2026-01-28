from app import db
from datetime import datetime

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True) # Optional link to course
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False) # Supports Markdown
    last_edited = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('notes', lazy=True))
    course = db.relationship('Course', backref=db.backref('notes', lazy=True))
