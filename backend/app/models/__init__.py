from app.models.user import User, EmailVerification
from app.models.course import Course, StudyKnowledge
from app.models.session import StudySession, ScheduleBlock
from app.models.note import Note
from app.models.system_alert import SystemAlert
from app.models.notification import Notification
from app.models.broadcast import Broadcast
from app.models.admin_broadcast import AdminBroadcast

# Join table for User-Course is now defined in app.models.course as UserCourse class
