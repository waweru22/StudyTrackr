from app import db
from app.models.session import StudySession
from app.models.course import Course
from app.models.broadcast import Broadcast
from datetime import datetime
from sqlalchemy import func

class AdminService:
    @staticmethod
    def get_low_focus_areas():
        # Avg distraction count by course
        # Join Session with Course
        results = db.session.query(
            Course.name,
            func.avg(StudySession.distraction_count).label('avg_distraction')
        ).join(Course, StudySession.course_id == Course.id)\
         .group_by(Course.name)\
         .order_by(func.avg(StudySession.distraction_count).desc())\
         .all()
         
        return [{'course': r.name, 'avg_distraction': round(r.avg_distraction, 2)} for r in results]

    @staticmethod
    def get_technique_impact():
        # Technique vs Success Score
        results = db.session.query(
            StudySession.learning_mode,
            func.avg(StudySession.success_score).label('avg_success')
        ).group_by(StudySession.learning_mode)\
         .all()
         
        return [{'technique': r.learning_mode, 'avg_success': round(r.avg_success, 2)} for r in results]

    @staticmethod
    def create_broadcast(admin_id, message, target_level):
        broadcast = Broadcast(
            admin_id=admin_id,
            message=message,
            target_level=target_level
        )
        db.session.add(broadcast)
        db.session.commit()
        return broadcast
