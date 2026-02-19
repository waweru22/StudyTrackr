from app import create_app, db
from app.models.user import User, EmailVerification
from app.models.course import UserCourse
from app.models.note import Note
from app.models.session import StudySession, ScheduleBlock
from app.models.broadcast import Broadcast
from app.models.system_alert import SystemAlert

app = create_app()

with app.app_context():
    print("Clearing user-related data...")
    
    # 1. Clear Dependent Tables (Child Tables first)
    print("Deleting System Alerts...")
    db.session.query(SystemAlert).delete()
    
    print("Deleting Broadcasts...")
    db.session.query(Broadcast).delete()
    
    print("Deleting Notes...")
    db.session.query(Note).delete()
    
    print("Deleting Study Sessions...")
    db.session.query(StudySession).delete()
    
    print("Deleting Schedule Blocks...")
    db.session.query(ScheduleBlock).delete()
    
    print("Deleting User Courses...")
    db.session.query(UserCourse).delete()
    
    print("Deleting Email Verifications...") # User creation depends on this sometimes, or vice versa?
    db.session.query(EmailVerification).delete()
    
    # 2. Clear Users
    print("Deleting Users...")
    db.session.query(User).delete()
    
    db.session.commit()
    print("Cleanup Complete. Curriculum (Courses) and Rules (Knowledge) preserved.")
