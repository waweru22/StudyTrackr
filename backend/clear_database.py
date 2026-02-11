from app import create_app, db
from app.models.user import User, EmailVerification
from app.models.session import StudySession, ScheduleBlock
from app.models.course import UserCourse, Course

app = create_app()

with app.app_context():
    print("Clearing all data...")
    try:
        # Delete dependent tables first
        db.session.query(ScheduleBlock).delete()
        db.session.query(StudySession).delete()
        db.session.query(UserCourse).delete()
        db.session.query(EmailVerification).delete()
        db.session.query(User).delete()
        # db.session.query(Course).delete() # Keep courses for testing? Or clear? Let's keep courses if they are seeded.
        
        db.session.commit()
        print("Data cleared!")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
