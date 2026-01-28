import requests
import json
import time

BASE_URL = 'http://localhost:5000'
ADMIN_EMAIL = 'admin_setup@nileuni.edu.ng'
ADMIN_PW = 'admin123'
STUDENT_EMAIL = f'student_alert_{int(time.time())}@example.com' # Unique
STUDENT_PW = 'password123'

def register_user(email, role='student', staff_id=None):
    url = f"{BASE_URL}/auth/admin/register" if role == 'admin' else f"{BASE_URL}/auth/onboard"
    payload = {
        'username': 'TestUser',
        'email': email,
        'password': STUDENT_PW,
        'confirm_password': STUDENT_PW
    }
    if role == 'admin':
        payload['status_id'] = staff_id
        # Admin flow handled separately in admin test.
        # Let's assume Student Onboard flow for alerts.
        pass
    else:
        payload['level'] = 100
        payload['selected_course_ids'] = [1]
        
    res = requests.post(f"{BASE_URL}/auth/onboard", json=payload)
    if res.status_code == 201:
        return res.json().get('access_token')
    
    # If exists, login via OTP
    otp_res = requests.post(f"{BASE_URL}/auth/request-otp", json={'email': email})
    if otp_res.status_code == 200:
        otp = otp_res.json().get('otp_debug')
        verify = requests.post(f"{BASE_URL}/auth/verify-otp", json={'email': email, 'otp_code': otp})
        return verify.json().get('access_token')
    return None

def test_alerts():
    print("Testing System Alerts & Dashboard...")
    token = register_user(STUDENT_EMAIL)
    if not token:
        print("Failed to get student token")
        return

    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Access Dashboard (Should be clean initially)
    print("\n[Test 1] Initial Dashboard")
    res = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Error Body: {res.text}")
    if res.status_code == 200:
        data = res.json()
        print(f"Feed Length: {len(data.get('feed', []))}")
        print(f"Featured Tip: {data.get('featured_tip', {}).get('title')}")
        if 'se_tip' in data.get('featured_tip', {}):
             print("PASS: Full Tip Dictionary Returned")
        else:
             print("FAIL: Full Tip missing")

    # 2. Mock Missed Session
    # We need to insert a ScheduleBlock in the past for today.
    # Since we can't easily insert via API (Schedule routes might allow?), 
    # we can try to use a script injection or assume we have 'create schedule' endpoint.
    # Assuming user has empty schedule. 
    # We need to access DB to insert a block.
    
    from app import create_app, db
    from app.models.session import ScheduleBlock
    from app.models.course import Course
    from app.models.user import User
    from datetime import datetime, timedelta, date, time as dtime
    
    app = create_app()
    with app.app_context():
        # Find user
        user = User.query.filter_by(email=STUDENT_EMAIL).first()
        if not user:
             print("User not found in DB!")
             return

        # Create Block in past (30 mins ago)
        # End time also past? Or current?
        now = datetime.utcnow()
        past_start = (now - timedelta(minutes=60)).time()
        past_end = (now - timedelta(minutes=30)).time()
        
        block = ScheduleBlock(
            user_id=user.id,
            course_id=1, # Assuming Course 1 exists
            day_of_week=now.strftime('%A'),
            date=now.date(),
            start_time=past_start,
            end_time=past_end,
            block_type='Deep Work'
        )
        db.session.add(block)
        db.session.commit()
        print("Mocked Past Schedule Block")

    # 3. Access Dashboard Again (Trigger Alert)
    print("\n[Test 2] Dashboard Trigger Alert")
    res = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    if res.status_code == 200:
        data = res.json()
        feed = data.get('feed', [])
        # Iterate feed to find alert
        found_alert = False
        for item in feed:
            if item.get('type') == 'alert' and 'missed' in item.get('message', '').lower():
                 found_alert = True
                 print(f"Alert Found: {item['message']}")
                 break
        
        if found_alert:
            print("PASS: SystemAlert generated and returned in feed")
        else:
            print(f"FAIL: Alert not found in feed. Feed: {feed}")

    # 4. Cleanup
    # Optional

if __name__ == "__main__":
    test_alerts()
