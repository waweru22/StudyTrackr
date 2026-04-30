import sys
import os
import time
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.session import ScheduleBlock
from app.services.inference_service import InferenceService

app = create_app()

def verify_expert_system():
    print("--- Verifying Expert System Inference ---")
    
    with app.app_context():
        # 1. Reset DB Schema for ScheduleBlock
        print("1. Updating Schema...")
        try:
            ScheduleBlock.__table__.drop(db.engine)
            db.create_all()
            print("   Schema Updated (ScheduleBlock recreated).")
        except Exception as e:
            print(f"   Schema update skipped/error: {e}")
            
        # 2. Setup Test User
        user = User.query.filter_by(email="verify_expert@test.com").first()
        if user:
            db.session.delete(user)
            db.session.commit()
            
        user = User(
            username="ExpertUser", 
            email="verify_expert@test.com", 
            password_hash="pw",
            peak_time="Morning", # Peak = Morning (09:00 slot)
            level=300
        )
        db.session.add(user)
        db.session.commit()
        
        # 3. Setup Courses (Mix of weights)
        # Heavy: Weight 5
        c_heavy = Course(code="HVY501", name="Heavy Logic", weight=5, credits=3) 
        # Light: Weight 1
        c_light = Course(code="LGT101", name="Light Intro", weight=1, credits=2)
        # Medium: Weight 3
        c_med = Course(code="MED301", name="Medium Core", weight=3, credits=3)
        
        db.session.add(c_heavy)
        db.session.add(c_light)
        db.session.add(c_med)
        user.courses.append(c_heavy)
        user.courses.append(c_light)
        user.courses.append(c_med)
        db.session.commit()
        
        print(f"   User Created. Peak: {user.peak_time}")
        print("   Courses Assigned: HVY501 (W5), LGT101 (W1), MED301 (W3)")
        
        # 4. Generate Schedule
        print("\n2. Generating Schedule...")
        InferenceService.generate_week_schedule(user.id)
        
        # 5. Verify Results
        blocks = ScheduleBlock.query.filter_by(user_id=user.id).order_by(ScheduleBlock.date, ScheduleBlock.start_time).all()
        print(f"   Generated {len(blocks)} blocks.")
        
        sunday_blocks = [b for b in blocks if b.day_of_week == 'Sunday']
        print(f"   Sunday Blocks: {len(sunday_blocks)}")
        if len(sunday_blocks) == 1 and "Behavioral" in sunday_blocks[0].technique_name:
            print("   ✅ Sunday Constraint Passed (Single Review Block w/ Technique).")
        else:
            print(f"   ❌ Sunday Constraint Failed. Found: {[b.technique_name for b in sunday_blocks]}")
            
        # Check Technique Assignment
        hvy_blocks = [b for b in blocks if b.course_id == c_heavy.id]
        if hvy_blocks and "Feynman" in hvy_blocks[0].technique_name:
            print(f"   ✅ Technique Assignment Passed (Heavy -> Feynman).")
        elif hvy_blocks:
            print(f"   ❌ Technique Assignment Failed. Heavy got: {hvy_blocks[0].technique_name}")
            
        lgt_blocks = [b for b in blocks if b.course_id == c_light.id]
        if lgt_blocks and ("Pomodoro" in lgt_blocks[0].technique_name or "Blurting" in lgt_blocks[0].technique_name):
            print(f"   ✅ Technique Assignment Passed (Light -> Pomodoro/Blurting).")
            
        # Check Energy Mapping (Heavy -> Morning)
        # user.peak_time = Morning (slot 0, 09:00)
        morning_hvy = [b for b in hvy_blocks if b.start_time.hour == 9]
        if len(morning_hvy) > 0:
            print(f"   ✅ Energy Mapping Passed (Heavy course scheduled at 09:00). Count: {len(morning_hvy)}")
        else:
            print(f"   ⚠️ Energy Mapping Warning. Heavy blocks at: {[b.start_time for b in hvy_blocks]}")
            
        # Check New Fields
        b = blocks[0]
        if b.status == 'pending' and b.technique_details:
             print("   ✅ Schema Verification Passed (status & technique_details exist).")
        else:
             print(f"   ❌ Schema Verification Failed. Status: {b.status}, Details: {b.technique_details}")

if __name__ == "__main__":
    verify_expert_system()
