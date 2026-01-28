from app import create_app, db
from app.models.course import Course
from app.models.user import User
from app.services.auth_service import AuthService
from flask import json

app = create_app()

def verify_alignment():
    print("--- Verifying Onboarding Alignment ---")
    
    with app.test_client() as client:
        # 1. Course Filter
        print("\n[Test 1] GET /courses?level=100")
        res = client.get('/courses/?level=100')
        print(f"Status: {res.status_code}")
        assert res.status_code == 200
        data = res.get_json()
        print(f"Found {len(data)} courses.")
        if data:
            print(f"Sample: {data[0]['code']} (Level {data[0]['level']})")
            assert data[0]['level'] == 100
            
    with app.app_context():
        # Setup Test Data for Validation
        # Ensure we have courses
        c100 = Course.query.filter_by(level=100).first()
        c400 = Course.query.filter_by(level=400).first()
        
        if not c100 or not c400:
            print("Skipping validation test: Test courses (L100/L400) not found in DB.")
            return

        print("\n[Test 2] Registration Level Validation")
        # Register L400 user with L100 course
        
        # Cleanup
        User.query.filter_by(email='mismatch@test.com').delete()
        db.session.commit()
        
        user_data = {
            'email': 'mismatch@test.com', 'username': 'MisMatcher', 'level': 400, 
            'password': 'SecurePassword123!', 'confirm_password': 'SecurePassword123!',
            'selected_course_ids': [c100.id] # Mismatch
        }
        
        user, msg = AuthService.register_user(user_data)
        print(f"Msg: {msg}")
        
        assert user is not None
        assert "Warnings:" in msg
        assert "does not match your level" in msg
        
        print("✅ Validation Warning Verified.")

if __name__ == '__main__':
    verify_alignment()
