from app import create_app, db
from app.models.user import User
from app.models.course import Course, StudyKnowledge
from app.models.session import ScheduleBlock
from app.services.inference_service import InferenceService
from app.services.session_service import SessionService
from datetime import time

app = create_app()

def verify_cognitive_logic():
    print("--- Verifying Cognitive Logic Modules ---")
    
    # Setup Test User
    db.session.query(ScheduleBlock).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    # 1. Active Recaller Identity Test
    print("\n[Test 1] Active Recaller Identity")
    user_ar = User(
        email="ar@test.com", username="AR", level=200, hashed_password="pw",
        base_template="Active Recaller", focus_threshold=60, peak_time="Morning"
    )
    db.session.add(user_ar)
    db.session.commit()
    
    courses = Course.query.limit(3).all()
    course_ids = [c.id for c in courses]
    
    InferenceService.generate_week_schedule(user_ar, course_ids)
    
    blocks = ScheduleBlock.query.filter_by(user_id=user_ar.id).limit(5).all()
    for b in blocks:
        duration = (b.end_time.hour - b.start_time.hour) * 60 + (b.end_time.minute - b.start_time.minute)
        print(f"Block Type: {b.block_type}, Duration: {duration}m")
        # Assert duration is 45m (Active Recaller constraint)
        if b.block_type == "Active Recall":
            assert duration == 45, f"Expected 45m, got {duration}m"
            
    # 2. Focus-Aware Scheduling (Threshold Filter)
    print("\n[Test 2] Focus Filter (Threshold < 60)")
    user_focus = User(
        email="focus@test.com", username="LowFocus", level=200, hashed_password="pw",
        base_template="Generic Learner", focus_threshold=45, peak_time="Afternoon"
    )
    db.session.add(user_focus)
    db.session.commit()
    
    # Pick a heavy course (Weight 5) which usually triggers Deep Work
    heavy_course = Course.query.filter_by(weight=5).first()
    if not heavy_course:
        print("Skipping Test 2: No weight 5 course found")
    else:
        InferenceService.generate_week_schedule(user_focus, [heavy_course.id])
        block = ScheduleBlock.query.filter_by(user_id=user_focus.id).first()
        print(f"Heavy Course Block Type: {block.block_type}")
        print(f"Reason: {block.refinement_reason}")
        
        assert block.block_type != "Deep Work", "Deep Work should be downgraded!"
        assert "intensity adjusted" in block.refinement_reason
        
    # 3. Cognitive Load Overflow
    print("\n[Test 3] Cognitive Load Overflow")
    # Using 'Deep Work Specialist' to force heavy blocks (1.5 cost)
    user_load = User(
        email="load@test.com", username="HeavyLoader", level=400, hashed_password="pw",
        base_template="Deep Work Specialist", focus_threshold=120, peak_time="Evening"
    )
    db.session.add(user_load)
    db.session.commit()
    
    # Adding many heavy courses to exceed daily budget (4.0)
    # 3 Deep Work blocks = 4.5 units -> Overflow
    # If using 7 days, we need enough to fill day 1. 
    # With 7 courses, day 0 gets one, day 1 gets one... wait.
    # The scheduling loop iterates 7 days. It assigns ONE course per day (primary).
    # Ah! The current implementation only schedules *one* core block per day in `generate_week_schedule`.
    # To test overflow, we need to artificially inject load into `daily_load_map` or modify `generate_week_schedule` to schedule multiple blocks/day.
    # OR, rely on the Retrieval Chain (which adds load to T+1).
    
    # Strategy: Pre-fill the daily_load_map in the Service (not possible easily)
    # OR: Realize that the current `generate_week_schedule` only adds ONE main block per day.
    # A Deep Work block is 1.5. Budget is 4.0. It will never overflow with just 1 block.
    # But... the Retrieval Chain adds to T+1.
    # If we have Day 1: Deep Work (1.5). T+1 gets Recall (1.0). Total Day 2 = 1.5 (Main) + 1.0 (Recall) = 2.5. Still under 4.0.
    
    # Conclusion: The current generator is too light for the budget test.
    # Fix for Verification: We can reduce the BUDGET constant in the test context?
    # InferenceService.DAILY_COGNITIVE_BUDGET = 1.0
    
    InferenceService.DAILY_COGNITIVE_BUDGET = 2.0 # Set budget to allow single Deep Work (1.5) but fail with Recall (1.0)
    heavy_courses = Course.query.filter_by(weight=5).limit(5).all()
    h_ids = [c.id for c in heavy_courses]
    
    InferenceService.generate_week_schedule(user_load, h_ids)
    
    # Check for overflow reason
    overflow_blocks = ScheduleBlock.query.filter(ScheduleBlock.refinement_reason.contains("Rescheduled due to Daily Cognitive Budget")).all()
    print(f"Overflow Blocks found: {len(overflow_blocks)}")
    if len(overflow_blocks) > 0:
        print("PASS: Cognitive Budget Logic triggered.")
    else:
        print("FAIL: No blocks rescheduled due to budget.")

if __name__ == '__main__':
    with app.app_context():
        verify_cognitive_logic()
