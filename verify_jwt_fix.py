from app import create_app
from app.models.user import User
from flask_jwt_extended import create_access_token
from flask import json

app = create_app()

def verify_jwt_fix():
    print("--- Verifying JWT Fix ---")
    
    with app.app_context():
        # Get a user
        user = User.query.first()
        if not user:
            print("No user found to test.")
            return

        # Create token with STRING identity (The Fix)
        token = create_access_token(identity=str(user.id))
        print(f"Generated Token for User {user.id} (Identity: String)")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        with app.test_client() as client:
            # Try a protected route: Dashboard
            print("\n[Test 1] GET /dashboard/")
            res = client.get('/dashboard/', headers=headers)
            print(f"Status: {res.status_code}")
            
            if res.status_code == 200:
                print("✅ Access Granted (Fix Worked)")
                data = res.get_json()
                print(f"XP: {data['xp']}")
            else:
                print(f"❌ Access Denied: {res.data}")
                
            # Try Protected POST: Session Start
            from app.models.course import Course
            course = Course.query.first()
            if not course:
                print("Skipping Session Test (No Course)")
            else:
                print(f"\n[Test 2] POST /session/start (Course {course.id})")
                res = client.post('/session/start', headers=headers, json={
                    'course_id': course.id, 
                    'learning_mode': 'Deep Work'
                })
                print(f"Status: {res.status_code}")
                if res.status_code in [201, 200]:
                    print("✅ Session Started")
                else:
                    print(f"❌ Session Failed: {res.data}")

if __name__ == '__main__':
    verify_jwt_fix()
