from app import create_app, db
from app.models.user import User
from app.models.course import Course, UserCourse
from app.models.session import ScheduleBlock, StudySession
from app.services.auth_service import AuthService
from app.services.inference_service import InferenceService
from datetime import datetime, time, date

app = create_app()

def verify_structural_updates():
    print("--- Verifying Model Restructuring ---")
    
    # Clean up test data
    db.session.query(ScheduleBlock).delete()
    db.session.query(UserCourse).delete()
    db.session.query(User).delete()
    db.session.commit()

    # 1. Verify User-Course Association & Limit
    print("\n[Test 1] User-Course Association & Limit")
    # Fetch 13 courses
    all_courses = Course.query.limit(13).all()
    if len(all_courses) < 13:
        print(f"Skipping limit test (only {len(all_courses)} courses in DB)")
        course_ids_ok = [c.id for c in all_courses[:5]]
    else:
        # Try registering with 13 courses
        course_ids_many = [c.id for c in all_courses]
        user_bad, msg = AuthService.register_user({
            'email': 'limit@test.com', 'username': 'limit', 'level': 100, 'password': 'password123', 'confirm_password': 'password123',
            'selected_course_ids': course_ids_many
        })
        print(f"Excess limit check: {msg}")
        assert user_bad is None
        assert "limit exceeded" in msg
        course_ids_ok = [c.id for c in all_courses[:5]]

    # Register valid user
    user_ok, msg = AuthService.register_user({
        'email': 'ok@test.com', 'username': 'okuser', 'level': 100, 'password': 'password123', 'confirm_password': 'password123',
        'selected_course_ids': course_ids_ok
    })
    print(f"Valid registration: {msg}")
    assert user_ok is not None
    # Verify association
    assert len(user_ok.courses) == len(course_ids_ok)
    print(f"User has {len(user_ok.courses)} courses linked.")

    # 2. Verify ScheduleBlock Date Logic
    print("\n[Test 2] ScheduleBlock Date & Match Helper")
    # Trigger inference for this user
    
    # Need to manually trigger because onboard calls generate_week_schedule but we didn't mock/check result there
    InferenceService.generate_week_schedule(user_ok) 
    
    block = ScheduleBlock.query.filter_by(user_id=user_ok.id).first()
    print(f"Generated Block: {block.day_of_week}, Date: {block.date}")
    assert block.date is not None
    assert isinstance(block.date, date)
    
    # Test Match Helper
    block_start_dt = datetime.combine(block.date, block.start_time)
    
    # Valid match (exact start)
    assert block.is_session_match(block_start_dt) == True
    print("Match Helper: Exact start -> True")
    
    # Valid match (+1 minute)
    assert block.is_session_match(block_start_dt.replace(minute=block_start_dt.minute+1)) == True
    
    # Invalid match (Wrong date)
    wrong_date = block_start_dt.replace(year=block_start_dt.year+1)
    assert block.is_session_match(wrong_date) == False
    print("Match Helper: Wrong Date -> False")
    
    print("✅ Model Restructuring Verified.")

if __name__ == '__main__':
    with app.app_context():
        verify_structural_updates()
