"""One-off: delete a user and related rows by username."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User, EmailVerification
from app.models.course import UserCourse, SavedResource
from app.models.session import StudySession, ScheduleBlock
from app.models.note import Note
from app.models.notification import Notification
from app.models.fcm_token import FCMToken
from app.models.adaptation_log import AdaptationLog
from app.models.timetable_entry import TimetableEntry
from app.models.system_alert import SystemAlert
from app.models.pending_registration import PendingRegistration

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "wawerulearns_"

app = create_app()
with app.app_context():
    user = User.query.filter_by(username=USERNAME).first()
    if not user:
        print(f"User {USERNAME!r} not found.")
        for u in User.query.with_entities(User.id, User.username, User.email).all():
            print(f"  id={u.id} username={u.username!r} email={u.email}")
        sys.exit(1)

    uid = user.id
    email = user.email
    print(f"Deleting id={uid} username={user.username!r} email={email}")

    StudySession.query.filter_by(user_id=uid).delete()
    ScheduleBlock.query.filter_by(user_id=uid).delete()
    TimetableEntry.query.filter_by(user_id=uid).delete()
    UserCourse.query.filter_by(user_id=uid).delete()
    SavedResource.query.filter_by(user_id=uid).delete()
    Note.query.filter_by(user_id=uid).delete()
    Notification.query.filter_by(user_id=uid).delete()
    FCMToken.query.filter_by(user_id=uid).delete()
    AdaptationLog.query.filter_by(user_id=uid).delete()
    SystemAlert.query.filter_by(user_id=uid).delete()
    EmailVerification.query.filter_by(email=email).delete()
    PendingRegistration.query.filter_by(email=email).delete()
    db.session.delete(user)
    db.session.commit()
    print("Done.")
