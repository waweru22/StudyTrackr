from app import create_app, db
from app.models.user import User
from app.models.session import StudySession
from app.services.session_service import SessionService
from datetime import datetime, timedelta

app = create_app()

def verify_variable_distraction():
    print("--- Verifying Variable Distraction Logic ---")
    
    with app.app_context():
        # Setup User & Session
        user = User.query.first()
        if not user:
            print("No user found.")
            return

        print(f"User ID: {user.id}")
        
        # Create Dummy Session
        session = StudySession(
            user_id=user.id,
            course_id=1,
            learning_mode='Deep Work',
            start_time=datetime.utcnow() - timedelta(minutes=60) # 60 min ago
        )
        db.session.add(session)
        db.session.commit()
        
        print(f"Session Started: {session.start_time}")
        print("Simulating 60m duration. Distractions: 240s (4m). Pause: 6m.")
        
        # End Session Data
        data = {
            'success_score': 90,
            'total_distraction_seconds': 240, # 4 mins
            'pause_duration': 6, # 6 mins
            'session_id': session.id
        }
        
        # Expected Net Duration = 60 - 4 - 6 = 50 mins
        # Expected XP = (50 / 90) * 100 = 55.55 -> 55
        
        s_end, xp = SessionService.end_session(session.id, data)
        
        if not s_end:
            print(f"Error: {xp}")
            return
            
        print(f"Final Duration (DB): {s_end.duration_minutes}m")
        print(f"XP Earned: {xp}")
        
        assert s_end.duration_minutes == 50
        assert xp == 55
        
        print("✅ Variable Distraction Logic Verified.")

if __name__ == '__main__':
    verify_variable_distraction()
