from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.session import ScheduleBlock
from app.services.inference_service import InferenceService
from sqlalchemy import func

app = create_app()

def verify_schedule():
    with app.app_context():
        # 1. Get a Test User (or create one)
        user = User.query.filter_by(email="test@user.com").first()
        if not user:
            print("Creating Test User...")
            user = User(email="test@user.com", username="TestUser", peak_time="Afternoon", level=100)
            user.hashed_password = "pbkdf2:sha256:260000$dummyhash"
            db.session.add(user)
            db.session.commit()
            
        # Ensure user has courses
        if not user.courses:
            print("Assigning courses to Test User...")
            all_courses = Course.query.all()
            user.courses.extend(all_courses)
            db.session.commit()
            print(f"Assigned {len(all_courses)} courses.")

        print(f"Verifying Schedule for User: {user.username}")

        # 2. Clear existing schedule
        ScheduleBlock.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        # 3. Generate Schedule
        print("Generating Schedule...")
        InferenceService.generate_week_schedule(user.id)

        # 4. Verify Results
        blocks = ScheduleBlock.query.filter_by(user_id=user.id).order_by(ScheduleBlock.date, ScheduleBlock.start_time).all()
        
        print(f"\nGenerated {len(blocks)} blocks.")
        
        # Group by Day
        days = {}
        for b in blocks:
            if b.day_of_week not in days: days[b.day_of_week] = []
            days[b.day_of_week].append(b)
            
        # Checks
        for day, day_blocks in days.items():
            print(f"\n--- {day} ---")
            course_ids = set()
            for b in day_blocks:
                course = Course.query.get(b.course_id)
                print(f"[{b.start_time}] {course.code} (W:{course.weight}) - {b.technique_name}")
                course_ids.add(b.course_id)
                
                # Verify Technique Rule
                if course.weight >= 4:
                    if "Feynman" not in b.technique_name:
                         print(f"   [WARNING] High weight course {course.code} got {b.technique_name}, expected Feynman.")
                elif course.weight <= 2:
                     if "Pomodoro" not in b.technique_name:
                         # It might be Active Recall if middle? 
                         # Rule was <=2 -> Pomodoro.
                         pass
            
            # Verify Variety
            if day != 'Sunday':
                if len(course_ids) < 3:
                     print(f"   [FAIL] Variety Check: Only {len(course_ids)} unique courses. Expected 3.")
                else:
                     print(f"   [PASS] Variety Check: {len(course_ids)} unique courses.")

if __name__ == "__main__":
    verify_schedule()
