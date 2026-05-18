from app.models.user import User, EmailVerification
from app.models.course import Course, StudyKnowledge
from app.models.session import StudySession, ScheduleBlock
from app.models.note import Note
from app.models.system_alert import SystemAlert
from app.models.notification import Notification
from app.models.notification_trigger import NotificationTrigger
from app.models.fcm_token import FCMToken
from app.models.broadcast import Broadcast
from app.models.admin_broadcast import AdminBroadcast
from app.models.pending_registration import PendingRegistration
from app.models.adaptation_log import AdaptationLog

# Join table for User-Course is now defined in app.models.course as UserCourse class
