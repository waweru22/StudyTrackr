from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app import db
from app.models.study_session import StudySession
from app.models.user import User
from app.services.notification_service import NotificationService

scheduler = BackgroundScheduler()

def check_upcoming_sessions():
    now = datetime.utcnow()
    reminder_window = now + timedelta(minutes=30)

    upcoming_sessions = StudySession.query.filter(
        StudySession.start_time >= now,
        StudySession.start_time <= reminder_window
    ).all()

    for session in upcoming_sessions:
        user = User.query.get(session.user_id)

        NotificationService.create_notification(
            user_id=user.id,
            title="Upcoming Study Session ⏰",
            message=f"You have a study session at {session.start_time}.",
            type="reminder",
            send_email_flag=True,
            user_email=user.email
        )

def start_scheduler():
    scheduler.add_job(check_upcoming_sessions, 'interval', minutes=10)
    scheduler.start()
