import sys
import os
import json

# Add backend to path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models.user import User, EmailVerification
from app.models.course import UserCourse

app = create_app()

def verify_flow():
    print("--- Verifying OTP Flow ---")
    client = app.test_client()
    
    email = "otp_test_8@example.com"
    password = "password123"
    
    with app.app_context():
        # Cleanup potential previous run
        print("   Cleaning up DB...")
        try:
            db.session.query(UserCourse).delete()
            db.session.query(EmailVerification).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("   DB Cleaned.")
        except Exception as e:
            db.session.rollback()
            print(f"   Cleanup Error: {e}")
    
    # 1. Onboard (Should NOT return token)
    print("1. Registering User...")
    payload = {
        "username": "OTPUser",
        "email": email,
        "password": password,
        "confirm_password": password,
        "level": 200,
        "semester_type": "harmattan",
        "selected_course_ids": [1, 2], # Assuming these IDs exist from seeding
        "peak_time": "Evening",
        "learning_style": "Visual",
        "environment_pref": "Library", 
        "focus_threshold": "45 mins",
        "place_of_study": "Library",
        "study_mode": "Deep Work"
    }
    
    resp = client.post('/auth/onboard', json=payload)
    print(f"   Onboard Status: {resp.status_code}")
    data = resp.get_json()
    
    if resp.status_code == 201:
        if 'access_token' not in data:
            print("   ✅ CORRECT: No access_token returned on onboard.")
        else:
            print("   ❌ FAILURE: access_token returned on onboard!")
            return
    else:
        print(f"   ❌ Onboard Failed: {data}")
        return

    # 2. Get OTP from DB
    print("2. Retrieving OTP from DB...")
    with app.app_context():
        otp_record = EmailVerification.query.filter_by(email=email).order_by(EmailVerification.expires_at.desc()).first()
        if not otp_record:
            print("   ❌ FAILURE: No OTP record found in DB!")
            return
        otp_code = otp_record.otp_code
        print(f"   OTP Found: {otp_code}")

    # 3. Verify OTP (Should return token)
    print(f"3. Verifying OTP {otp_code}...")
    verify_payload = {
        "email": email,
        "otp_code": otp_code
    }
    
    resp = client.post('/auth/verify-otp', json=verify_payload)
    print(f"   Verify Status: {resp.status_code}")
    data = resp.get_json()
    
    token = None
    if resp.status_code == 200:
        if 'access_token' in data and 'user_id' in data:
            token = data['access_token']
            print("   ✅ CORRECT: access_token and user_id returned.")
        else:
             print(f"   ❌ FAILURE: Token or User ID missing. Got keys: {list(data.keys())}")
             return
    else:
        print(f"   ❌ Verify Failed: {data}")
        return

    # 4. Access Protected Route
    print("4. Accessing Protected Route (/schedule)...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = client.get('/schedule', headers=headers)
    print(f"   Schedule Status: {resp.status_code}")
    if resp.status_code == 200:
        print("   ✅ CORRECT: Protected route accessed successfully.")
    else:
        print(f"   ❌ FAILURE: Could not access schedule. {resp.get_json()}")

if __name__ == "__main__":
    verify_flow()
