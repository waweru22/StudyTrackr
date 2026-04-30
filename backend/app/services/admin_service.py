from app import db
from app.models.user import User
from app.models.session import StudySession, ScheduleBlock
from app.models.course import Course
from app.models.notification import Notification
from app.models.admin_broadcast import AdminBroadcast
from app.services.notification_service import NotificationService
from app.services.mail_service import MailService
from datetime import datetime, timedelta
from sqlalchemy import func


class AdminService:
    # ─── Dashboard Metrics ───────────────────────────────────────────

    @staticmethod
    def get_dashboard_metrics(weeks=1):
        now = datetime.utcnow()
        cutoff = now - timedelta(weeks=weeks)

        # Total verified students
        total_students = User.query.filter(
            User.role == 'student',
            User.is_verified == True
        ).count()

        # Pending verification
        pending_count = User.query.filter(
            User.role == 'student',
            User.is_verified == False
        ).count()

        # Session metrics (within time window)
        session_query = StudySession.query.filter(
            StudySession.start_time >= cutoff,
            StudySession.end_time.isnot(None)
        )

        total_sessions = session_query.count()

        avg_focus = db.session.query(
            func.avg(StudySession.success_score)
        ).filter(
            StudySession.start_time >= cutoff,
            StudySession.end_time.isnot(None)
        ).scalar() or 0

        avg_duration = db.session.query(
            func.avg(StudySession.duration_minutes)
        ).filter(
            StudySession.start_time >= cutoff,
            StudySession.end_time.isnot(None)
        ).scalar() or 0

        # Top 5 techniques (from ScheduleBlock)
        technique_rows = db.session.query(
            ScheduleBlock.technique_name,
            func.count(ScheduleBlock.id).label('usage_count')
        ).filter(
            ScheduleBlock.technique_name.isnot(None),
            ScheduleBlock.technique_name != '',
            ScheduleBlock.created_at >= cutoff
        ).group_by(ScheduleBlock.technique_name)\
         .order_by(func.count(ScheduleBlock.id).desc())\
         .limit(5).all()

        top_techniques = [
            {'technique_name': r.technique_name, 'usage_count': r.usage_count}
            for r in technique_rows
        ]

        # Top 5 courses by session frequency
        course_rows = db.session.query(
            Course.id,
            Course.code,
            Course.name,
            func.count(StudySession.id).label('session_count')
        ).join(StudySession, StudySession.course_id == Course.id)\
         .filter(StudySession.start_time >= cutoff)\
         .group_by(Course.id, Course.code, Course.name)\
         .order_by(func.count(StudySession.id).desc())\
         .limit(5).all()

        top_courses = [
            {'course_id': r.id, 'course_code': r.code, 'course_name': r.name, 'session_count': r.session_count}
            for r in course_rows
        ]

        return {
            'total_students': total_students,
            'total_sessions_completed': total_sessions,
            'avg_focus_score': round(float(avg_focus), 2),
            'avg_session_duration': round(float(avg_duration), 1),
            'top_techniques': top_techniques,
            'top_courses': top_courses,
            'student_verification_pending': pending_count
        }

    # ─── Course CRUD ─────────────────────────────────────────────────

    @staticmethod
    def list_courses():
        courses = Course.query.order_by(Course.level.asc(), Course.code.asc()).all()
        return [{
            'id': c.id,
            'code': c.code,
            'name': c.name,
            'level': c.level,
            'semester': c.semester,
            'credits': c.credits,
            'weight': c.weight,
            'is_active': c.is_active
        } for c in courses]

    @staticmethod
    def create_course(data):
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        credits = data.get('credits', 3)
        weight = data.get('weight', 1)
        level = data.get('level', 100)
        semester = data.get('semester', 1)

        # Validate uniqueness
        if Course.query.filter_by(code=code).first():
            return None, "Course code already exists"

        # Validate ranges
        if not (1 <= int(credits) <= 4):
            return None, "Credits must be between 1 and 4"
        if not (1 <= int(weight) <= 5):
            return None, "Weight must be between 1 and 5"

        course = Course(
            code=code, name=name, level=level,
            semester=semester, credits=credits, weight=weight
        )
        db.session.add(course)
        db.session.commit()
        return course, "Course created"

    @staticmethod
    def update_course(course_id, data):
        course = Course.query.get(course_id)
        if not course:
            return None, "Course not found"

        if 'code' in data:
            existing = Course.query.filter(Course.code == data['code'], Course.id != course_id).first()
            if existing:
                return None, "Course code already exists"
            course.code = data['code']
        if 'name' in data:
            course.name = data['name']
        if 'level' in data:
            course.level = data['level']
        if 'semester' in data:
            course.semester = data['semester']
        if 'credits' in data:
            if not (1 <= int(data['credits']) <= 4):
                return None, "Credits must be between 1 and 4"
            course.credits = data['credits']
        if 'weight' in data:
            if not (1 <= int(data['weight']) <= 5):
                return None, "Weight must be between 1 and 5"
            course.weight = data['weight']

        db.session.commit()
        return course, "Course updated"

    @staticmethod
    def delete_course(course_id):
        """Soft-delete: sets is_active=False to preserve historical data."""
        course = Course.query.get(course_id)
        if not course:
            return None, "Course not found"

        course.is_active = False
        db.session.commit()
        return course, "Course deactivated (soft-deleted)"

    # ─── Student Verification ────────────────────────────────────────

    @staticmethod
    def get_unverified_students():
        students = User.query.filter(
            User.role == 'student',
            User.is_verified == False
        ).order_by(User.created_at.desc()).all()

        return [{
            'id': s.id,
            'email': s.email,
            'username': s.username,
            'level': s.level,
            'registration_date': s.created_at.isoformat() if s.created_at else None
        } for s in students]

    @staticmethod
    def approve_student(student_id):
        student = User.query.filter_by(id=student_id, role='student').first()
        if not student:
            return None, "Student not found"

        student.is_verified = True
        db.session.commit()

        # Create notification
        NotificationService.create_notification(
            student.id,
            "Account Verified ✅",
            "Your account has been verified by an administrator. You can now view your study schedule.",
            type="system"
        )

        # Send email
        try:
            MailService.send_verification_approved_email(student.email)
        except Exception as e:
            print(f"[AdminService] Email send failed for {student.email}: {e}")

        return student, "Student approved"

    @staticmethod
    def reject_student(student_id):
        student = User.query.filter_by(id=student_id, role='student').first()
        if not student:
            return None, "Student not found"

        email = student.email
        db.session.delete(student)
        db.session.commit()
        return {'email': email}, "Student rejected and removed"

    # ─── Course Analytics ────────────────────────────────────────────

    @staticmethod
    def get_course_analytics(level=None, weeks=None):
        query = db.session.query(
            Course.id,
            Course.name,
            Course.code,
            func.count(StudySession.id).label('total_sessions'),
            func.avg(StudySession.success_score).label('avg_success_score'),
            func.avg(User.focus_threshold).label('avg_focus_level'),
            func.sum(
                db.case(
                    (StudySession.success_score < 3, 1),
                    else_=0
                )
            ).label('low_performers')
        ).outerjoin(StudySession, StudySession.course_id == Course.id)\
         .outerjoin(User, User.id == StudySession.user_id)

        if level:
            # Filter by student level
            query = query.filter(User.level == int(level))

        if weeks:
            cutoff = datetime.utcnow() - timedelta(weeks=int(weeks))
            query = query.filter(StudySession.start_time >= cutoff)

        # Exclude admin users from analytics
        query = query.filter(
            db.or_(User.role == 'student', User.id.is_(None))
        )

        results = query.group_by(Course.id, Course.name, Course.code)\
                       .order_by(func.sum(
                           db.case((StudySession.success_score < 3, 1), else_=0)
                       ).desc())\
                       .all()

        return [{
            'course_id': r.id,
            'course_name': r.name,
            'course_code': r.code,
            'total_sessions': r.total_sessions or 0,
            'avg_success_score': round(float(r.avg_success_score or 0), 2),
            'avg_focus_level': round(float(r.avg_focus_level or 0), 1),
            'low_performers': int(r.low_performers or 0)
        } for r in results]

    # ─── Technique Effectiveness ─────────────────────────────────────

    @staticmethod
    def get_technique_effectiveness():
        # Global average
        global_avg = db.session.query(
            func.avg(StudySession.success_score)
        ).filter(StudySession.end_time.isnot(None)).scalar() or 0
        global_avg = float(global_avg)

        # Per-technique stats using ScheduleBlock.technique_name joined with StudySession
        results = db.session.query(
            ScheduleBlock.technique_name,
            func.count(ScheduleBlock.id).label('usage_count'),
            func.avg(StudySession.success_score).label('avg_success_score')
        ).outerjoin(
            StudySession,
            db.and_(
                StudySession.course_id == ScheduleBlock.course_id,
                StudySession.user_id == ScheduleBlock.user_id
            )
        ).filter(
            ScheduleBlock.technique_name.isnot(None),
            ScheduleBlock.technique_name != ''
        ).group_by(ScheduleBlock.technique_name)\
         .order_by(func.count(ScheduleBlock.id).desc())\
         .all()

        return [{
            'technique_name': r.technique_name,
            'usage_count': r.usage_count,
            'avg_success_score': round(float(r.avg_success_score or 0), 2),
            'avg_focus_impact': round(float(r.avg_success_score or 0) - global_avg, 2)
        } for r in results]

    # ─── Broadcast System ────────────────────────────────────────────

    @staticmethod
    def send_broadcast(admin_id, admin_email, title, message, target_level=None):
        # 1. Create AdminBroadcast record
        broadcast = AdminBroadcast(
            admin_id=admin_id,
            title=title,
            message=message,
            target_level=target_level,
            created_by=admin_email
        )
        db.session.add(broadcast)
        db.session.flush()

        # 2. Find target students
        student_query = User.query.filter(User.role == 'student')
        if target_level:
            student_query = student_query.filter(User.level == int(target_level))
        students = student_query.all()

        # 3. Create notifications for each student
        notification_count = 0
        for student in students:
            NotificationService.create_notification(
                student.id, title, message, type='admin_broadcast'
            )
            notification_count += 1

        # 4. Send emails (best effort)
        for student in students:
            try:
                MailService.send_broadcast_email(student.email, title, message)
            except Exception as e:
                print(f"[Broadcast] Email failed for {student.email}: {e}")

        db.session.commit()
        return broadcast, notification_count

    @staticmethod
    def get_broadcast_history():
        broadcasts = AdminBroadcast.query.order_by(
            AdminBroadcast.created_at.desc()
        ).all()
        return [b.to_dict() for b in broadcasts]

    # ─── Legacy methods (kept for backward compat) ───────────────────

    @staticmethod
    def get_low_focus_areas():
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
        results = db.session.query(
            StudySession.learning_mode,
            func.avg(StudySession.success_score).label('avg_success')
        ).group_by(StudySession.learning_mode).all()
        return [{'technique': r.learning_mode, 'avg_success': round(r.avg_success, 2)} for r in results]
