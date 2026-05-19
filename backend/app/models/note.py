from app import db
from datetime import datetime

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True) # Optional link to course
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False) # Supports Markdown
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_edited = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    file_path = db.Column(db.String(300), nullable=True) # For file uploads
    file_type = db.Column(db.String(10), nullable=False, default='pdf')  # 'pdf' or 'html'
    annotation = db.Column(db.Text, nullable=True)  # User annotations on uploaded documents

    user = db.relationship('User', backref=db.backref('notes', lazy=True))
    course = db.relationship('Course', backref=db.backref('notes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'annotation': self.annotation or '',
            'last_edited': self.last_edited.isoformat()
        }
