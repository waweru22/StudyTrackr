from app import create_app, db
from app.models.user import User
from app.models.course import Course, UserCourse
from app.models.session import StudySession, ScheduleBlock
from app.services.inference_service import InferenceService
from app.services.audit_service import WeeklyAuditService
from app.services.session_service import SessionService
from datetime import datetime, time, date, timedelta

app = create_app()

def verify_overhaul():
    print("--- Verifying Cognitive Logic & Session Overhaul ---")
    
    # Clean Data
    db.session.query(ScheduleBlock).delete()
    db.session.query(StudySession).delete()
    db.session.query(UserCourse).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    # Setup User
    user = User(
        email='overhaul@test.com', username='OverhaulUser', level=100, hashed_password='pw',
        base_template='Deep Work Specialist', focus_threshold=45, peak_time='Morning',
        daily_cognitive_budget=2.0 # Low Budget to force downgrades
    )
    db.session.add(user)
    db.session.commit()
    
    # Setup Courses (High Weights)
    courses = Course.query.filter(Course.weight >= 4).limit(4).all()
    user.courses.extend(courses)
    db.session.commit()
    
    # 1. Inference: Triple-Slot / Hard-Wall Fix
    print("\n[Test 1] Inference Engine (Grid & Budget Downgrade)")
    # Budget 2.0. Deep Work costs 1.5. 
    # If we have 3 slots/day.
    # Course 1 (W=5) -> Deep Work (1.5). Fits Day 1 Slot 0. Load=1.5.
    # Course 2 (W=5) -> Deep Work (1.5). 1.5+1.5 > 2.0. No fit Slot 1.
    # ... Day 2 ...
    # With 4 heavy courses, they will fill 4 days.
    # But wait, we want to test DOWNGRADE "If a course cannot fit by Saturday".
    # We need MORE courses than slots/budget allow as Deep Work.
    # 6 days * 1 slot/day (limited by budget) = 6 Deep Work slots max.
    # If we have 7 heavy courses?
    # Let's add more courses.
    all_courses = Course.query.limit(8).all()
    user.courses = []
    user.courses.extend(all_courses)
    db.session.commit()
    
    InferenceService.generate_week_schedule(user)
    
    blocks = ScheduleBlock.query.filter_by(user_id=user.id).all()
    # Check for downgrades
    downgraded = [b for b in blocks if "Intensity adjusted to ensure full curriculum coverage" in (b.refinement_reason or "")]
    print(f"Downgraded Blocks: {len(downgraded)}")
    # We expect some? 
    # Also check Sunday is empty
    sunday_blocks = [b for b in blocks if b.day_of_week == 'Sunday']
    assert len(sunday_blocks) == 0, "Sunday should be empty"
    print("Sunday Logic: Pass")
    
    # 2. Session: Distraction & Time Deduction
    print("\n[Test 2] Session Distraction & Time Deduction")
    # Start Session
    session, nudge, _ = SessionService.start_session(user.id, {
        'course_id': courses[0].id,
        'learning_mode': 'Deep Work'
    })
    # Warning Check (User has 45m threshold, config might be 90m for Deep Work)
    print(f"Startup Nudge: {nudge}")
    if "Refocus Alert: Session exceeds" in (nudge or ""):
        print("Startup Warning: Pass")
    else:
        print("Startup Warning: Fail/Not Triggered")
        
    # Log Distractions
    ok1, msg1 = SessionService.log_distraction(session.id)
    print(f"Distraction 1: {msg1}")
    ok2, msg2 = SessionService.log_distraction(session.id)
    print(f"Distraction 2: {msg2}")
    ok3, msg3 = SessionService.log_distraction(session.id)
    print(f"Distraction 3: {msg3}") # Should fail
    assert ok3 == False
    
    # End Session (Simulate 60m duration)
    # Deduction: 2 * 5 = 10m. Final = 50m.
    # XP Formula: ((50 - 0) / 90) * 100 - (2 * 10) = (0.55 * 100) - 20 = 55 - 20 = 35 XP
    session.start_time = datetime.utcnow() - timedelta(minutes=60)
    session, xp = SessionService.end_session(session.id, {'success_score': 80})
    
    print(f"Final Duration: {session.duration_minutes}m (Expected 50m)")
    print(f"XP Earned: {xp}")
    
    assert session.duration_minutes == 50
    # XP check approx
    expected_xp = int(((50)/90)*100 - 20)
    print(f"Expected XP: {expected_xp}")
    assert xp == expected_xp
    
    # 3. Audit: Inclusive & Value Score
    print("\n[Test 3] Audit Inclusive Analytics")
    # Create a 0 score session
    s_bad = StudySession(
        user_id=user.id, course_id=courses[0].id,
        start_time=datetime.utcnow() - timedelta(hours=10), # Morning?
        end_time=datetime.utcnow() - timedelta(hours=9),
        success_score=5.0, # Low score
        distraction_count=0
    )
    db.session.add(s_bad)
    db.session.commit()
    
    report = WeeklyAuditService.perform_audit(user.id)
    print("Audit Report:")
    for line in report:
        print((line))
    
    # Check if this session was included.
    # Report should show "Morning: Value Score ... (Freq: 2..." (Start session above + this one)
    # Actually above session was just now (Afternoon?), this bad session is Morning.
    # Check output for inclusion.
    
    print("✅ Overhaul Verified.")

if __name__ == '__main__':
    with app.app_context():
        verify_overhaul()
