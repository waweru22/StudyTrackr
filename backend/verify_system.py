import os
from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.timetable_entry import TimetableEntry
from app.models.session import ScheduleBlock, StudySession
from app.services.inference_service import InferenceService
from app.services.session_service import SessionService
from werkzeug.security import generate_password_hash
from datetime import datetime, time

app = create_app()

def verify_system_internal():
    print("=== STUDYTRACKR SYSTEM VERIFICATION ===")
    
    with app.app_context():
        # 1. Create a verified test user
        test_email = 'system_verify@nileuniversity.edu.ng'
        user = User.query.filter_by(email=test_email).first()
        if user:
            # Clean up old data
            TimetableEntry.query.filter_by(user_id=user.id).delete()
            ScheduleBlock.query.filter_by(user_id=user.id).delete()
            StudySession.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
            
        courses = Course.query.filter_by(level=200, semester=1).limit(3).all()
        
        user = User(
            username='sys_tester',
            email=test_email,
            hashed_password=generate_password_hash('Password123!'),
            level=200,
            role='student',
            is_verified=True,
            base_template='balanced_sprinter',
            peak_time='morning',
            focus_threshold=60,
            learning_style='read_write'
        )
        for c in courses:
            user.courses.append(c)
            
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        print(f"[OK] User created: {test_email}")
        
        # 2. Add Mock Timetable Entries
        if courses:
            t1 = TimetableEntry(user_id=user_id, course_code=courses[0].code, course_name=courses[0].name, day_of_week='Monday', start_time=time(9,0), end_time=time(11,0))
            t2 = TimetableEntry(user_id=user_id, course_code=courses[1].code, course_name=courses[1].name, day_of_week='Wednesday', start_time=time(14,0), end_time=time(16,0))
            db.session.add_all([t1, t2])
            db.session.commit()
            print("[OK] Timetable entries seeded.")
        else:
            print("[FAIL] No courses found in database.")
            return

        # 3. Test Schedule Generation (Inference Service)
        print("Running Inference Engine...")
        InferenceService.generate_week_schedule(user_id)
        
        blocks = ScheduleBlock.query.filter_by(user_id=user_id).all()
        if blocks:
            print(f"[OK] Schedule Generation: {len(blocks)} study blocks generated automatically.")
            # Print a sample block
            print(f"     Sample: {blocks[0].date} {blocks[0].start_time}-{blocks[0].end_time} | {blocks[0].course.code} | {blocks[0].technique_name}")
        else:
            print("[FAIL] Schedule Generation produced 0 blocks.")
            return
            
        # 4. Test Session Service (Rule Engine + Gamification)
        block = blocks[0]
        
        # Start session
        session, nudge, tech_info = SessionService.start_session(
            user_id,
            {
                "course_id": block.course_id,
                "vibe": "High Energy",
                "social_setting": "Solo",
                "learning_mode": block.technique_name,
                "environment": "Library"
            }
        )
        
        if session:
            print(f"[OK] Session Start | Rule Engine matched context. Nudge: {nudge}")
        else:
            print("[FAIL] Session Start failed.")
            return
            
        # Log distraction
        SessionService.log_distraction(session.id)
        print("[OK] Distraction logged.")
        
        # End session
        ended_session, xp = SessionService.end_session(
            session.id,
            {
                "success_score": 4,
                "mood_after": 3,
                "actual_duration_minutes": 45,
                "completed_on_time": True,
                "total_distraction_seconds": 30,
                "would_repeat": True
            }
        )
        
        if ended_session:
            print(f"[OK] Session End | Gamification Engine awarded {xp} XP.")
        else:
            print("[FAIL] Session End failed.")
            
        print("=== VERIFICATION COMPLETE ===")

if __name__ == '__main__':
    verify_system_internal()
