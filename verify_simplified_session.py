import requests
import json
import random

BASE_URL = 'http://localhost:5000'
EMAIL = 'simplified_test@example.com'
PASSWORD = 'password123'

def get_auth_token():
    print(f"Attempting valid authentication for {EMAIL}...")
    
    # 1. Try Onboarding (Registration)
    onboard_payload = {
        'username': 'SimplifiedTest',
        'email': EMAIL,
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'level': 'Undergraduate',
        'selected_course_ids': [1], # Will verify/fetch valid course later if needed
        'focus_interval': 25,
        'identity_label': 'Scholar',
        'cognitive_style': 'Mix',
        'preferred_environment': 'Quiet'
    }
    
    res = requests.post(f"{BASE_URL}/auth/onboard", json=onboard_payload)
    
    if res.status_code == 201:
        print("Onboarding successful.")
        return res.json().get('access_token')
        
    error_msg = res.json().get('error', '')
    if "already registered" in error_msg or "exists" in error_msg or res.status_code == 400:
        print("User likely exists, trying OTP login flow...")
        
        # Request OTP
        otp_res = requests.post(f"{BASE_URL}/auth/request-otp", json={'email': EMAIL})
        if otp_res.status_code != 200:
            print(f"Failed to request OTP: {otp_res.text}")
            return None
            
        otp_code = otp_res.json().get('otp_debug')
        print(f"Got OTP: {otp_code}")
        
        # Verify OTP
        verify_res = requests.post(f"{BASE_URL}/auth/verify-otp", json={
            'email': EMAIL,
            'otp_code': otp_code
        })
        
        if verify_res.status_code == 200:
            print("OTP Verification successful.")
            return verify_res.json().get('access_token')
        else:
            print(f"OTP Verification failed: {verify_res.text}")
            return None
            
    return None

def get_valid_course_id():
    res = requests.get(f"{BASE_URL}/courses/all")
    if res.status_code == 200:
        courses = res.json()
        if courses:
            return courses[0]['id']
    return 1

def test_simplified_session_tracking():
    print("Testing Simplified Session Tracking...")
    
    token = get_auth_token()
    if not token:
        print("Failed to get auth token.")
        return

    headers = {'Authorization': f'Bearer {token}'}
    
    course_id = get_valid_course_id()
    print(f"Using Course ID: {course_id}")
    
    # 2. Start Session
    start_payload = {
        'course_id': course_id,
        'learning_mode': 'Deep Work',
        'session_goal': 'Test Simplified Tracking'
    }
    start_res = requests.post(f"{BASE_URL}/session/start", json=start_payload, headers=headers)
    if start_res.status_code != 201:
        print(f"Start Session failed: {start_res.text}")
        return
        
    session_id = start_res.json().get('session_id')
    print(f"Session Started: ID {session_id}")
    
    # 3. End Session with distraction
    distraction_seconds = 300 # 5 minutes
    
    end_payload = {
        'session_id': session_id,
        'total_distraction_seconds': distraction_seconds,
        'success_score': 0.8
    }
    
    end_res = requests.post(f"{BASE_URL}/session/end", json=end_payload, headers=headers)
    
    print(f"End Session Response Code: {end_res.status_code}")
    print(f"End Session Response Body: {end_res.text}")
    
    if end_res.status_code == 200:
        data = end_res.json()
        if 'pause_duration' in data:
            print("FAIL: pause_duration present in response")
        else:
            print("PASS: pause_duration not in response")
            
        print(f"Duration: {data.get('duration_minutes')}")
        print(f"XP Earned: {data.get('xp_earned')}")
        
        if data.get('xp_earned') is not None:
             print("PASS: XP returned")
        else:
             print("FAIL: XP missing")

if __name__ == "__main__":
    try:
        test_simplified_session_tracking()
    except Exception as e:
        print(f"Error: {e}")
