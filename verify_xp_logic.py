import requests
import json

BASE_URL = 'http://localhost:5000'
EMAIL = 'xp_test@example.com' 
PASSWORD = 'password123'

def get_auth_token():
    # Helper to get token (register/login)
    try:
        res = requests.post(f"{BASE_URL}/auth/onboard", json={
            'username': 'XPTestUser',
            'email': EMAIL,
            'password': PASSWORD,
            'confirm_password': PASSWORD,
            'level': 'Master',
            'selected_course_ids': [1]
        })
        if res.status_code == 201:
            return res.json().get('access_token')
            
        # If exists, login via OTP flow
        otp_res = requests.post(f"{BASE_URL}/auth/request-otp", json={'email': EMAIL})
        otp_code = otp_res.json().get('otp_debug')
        verify_res = requests.post(f"{BASE_URL}/auth/verify-otp", json={
            'email': EMAIL, 
            'otp_code': otp_code
        })
        return verify_res.json().get('access_token')
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def test_xp_logic():
    print("Testing XP Calculation Logic...")
    token = get_auth_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Start Session
    start_res = requests.post(f"{BASE_URL}/session/start", json={
        'course_id': 1, 'learning_mode': 'Deep Work'
    }, headers=headers)
    session_id = start_res.json().get('session_id')
    print(f"Session Started: {session_id}")
    
    # 2. Test Anomaly Guard
    # Distraction > Duration (Since we just started, duration is ~0)
    print("\n[Test 1] Anomalous Data Check")
    end_res_fail = requests.post(f"{BASE_URL}/session/end", json={
        'session_id': session_id,
        'total_distraction_seconds': 99999, # Huge distraction
        'success_score': 0.5
    }, headers=headers)
    
    print(f"Status: {end_res_fail.status_code}")
    print(f"Body: {end_res_fail.text}")
    try:
        data_fail = end_res_fail.json()
    except:
        print("Failed to decode JSON")
        data_fail = {}
        
    print(f"Duration (Should be 0): {data_fail.get('duration_minutes')}")
    if data_fail.get('duration_minutes') == 0:
        print("PASS: Anomalous data handled (duration set to 0)")
    else:
        print("FAIL: Anomalous data not handled")

    # 3. Test XP Calculation
    # We need a fresh session for clean test or just reuse if allowed.
    # Let's start a new one to mimic a real flow better.
    start_res_2 = requests.post(f"{BASE_URL}/session/start", json={
        'course_id': 1, 'learning_mode': 'Deep Work'
    }, headers=headers)
    sid_2 = start_res_2.json().get('session_id')
    
    # Mocking: We can't wait 90 minutes.
    # However, SessionService calculates "raw_duration" from timestamps.
    # To test the MATH, we have to rely on what `end_session` calculates.
    # Since we can't spoof `start_time` easily via API, `raw_duration` will be ~0.
    # 0 mins - distraction = 0. Base XP = 0.
    # This makes verifying the formula hard without unit tests or mocking.
    
    # Alternative: We can verify the PENALTY logic if we had base XP.
    # But with 0 base XP, penalty makes it 0.
    
    # Wait, the user wants me to verify logic.
    # I should perhaps spoof the `start_time` in the DB directly?
    # I can use a script to update the DB directly?
    # Yes, since I'm running locally.
    
    print("\n[Test 2] XP Formula Verification (with DB Mocking)")
    # Update start_time to 90 mins ago
    from app import create_app, db
    from app.models.session import StudySession
    from datetime import datetime, timedelta
    
    app = create_app()
    with app.app_context():
        session = StudySession.query.get(sid_2)
        session.start_time = datetime.utcnow() - timedelta(minutes=90)
        db.session.commit()
        print("Mocked session start_time to -90 mins")
        
    # Now End Session
    # Duration: 90 mins
    # Distraction: 1 count, 10 mins (600s)
    # Net: 90 - 10 = 80 mins
    # Base XP: (80/90)*100 = 88.88 -> 88 XP? Or check rounding? `int(max(0, base_xp - penalty))`
    # Wait, Base XP calculation in code: `(net_duration / 90.0) * 100.0`
    # (80/90)*100 = 88.888...
    # Penalty: 1 count * 10 = 10 XP
    # Final: int(88.88 - 10) = int(78.88) = 78 XP.
    
    # Note: `distraction_count` is incremented by `/nudge` or manual update?
    # The `StudySession` model has `distraction_count`.
    # I need to set that too if valid.
    # The endpoint `/session/end` doesn't take distraction_count (it comes from session state).
    # Does `end_session` update distraction count from payload? NO.
    # It assumes it was tracked during session.
    # I need to mock distraction_count too.
    
    with app.app_context():
        session = StudySession.query.get(sid_2)
        session.distraction_count = 1
        db.session.commit()
        print("Mocked session distraction_count to 1")

    end_res_2 = requests.post(f"{BASE_URL}/session/end", json={
        'session_id': sid_2,
        'total_distraction_seconds': 600, # 10 mins
        'success_score': 1.0
    }, headers=headers)
    
    d2 = end_res_2.json()
    print(f"XP Earned: {d2.get('xp_earned')}")
    print(f"Duration: {d2.get('duration_minutes')}")
    
    expected_xp = 78
    if d2.get('xp_earned') == expected_xp:
        print(f"PASS: XP matches expected {expected_xp}")
    else:
        print(f"FAIL: XP {d2.get('xp_earned')} != {expected_xp}")

if __name__ == "__main__":
    test_xp_logic()
