import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def get_token():
    # Login to get token
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "audit_test_user@nileuniversity.edu.ng", # Assuming this user exists from previous turn? or I should register fresh.
        # Actually I can't guarantee this user exists. Re-registering might be safer or using a hardcoded one if verify_users.py showed one.
        # Let's try a safe new user.
        "password": "TestPassword123"
    })
    if resp.status_code == 200:
        return resp.json()['access_token']
    
    # Try Registering
    print("Login failed, registering new user...")
    reg_resp = requests.post(f"{BASE_URL}/auth/onboard", json={
        "email": "auto_schedule_test@nile.edu.ng",
        "username": "auto_schedule_test",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "level": 200,
        "selected_course_ids": [1, 2] # Assuming courses exist
    })
    if reg_resp.status_code in [200, 201]:
        return reg_resp.json()['access_token']
    
    print(f"Registration failed: {reg_resp.text}")
    return None

def test_schedule():
    token = get_token()
    if not token:
        print("FAIL: Could not authenticate")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Testing GET /schedule (Inference Trigger) ---")
    resp = requests.get(f"{BASE_URL}/schedule/", headers=headers)
    
    if resp.status_code == 200:
        schedule = resp.json()
        print(f"PASS: Schedule Retrieved. Count: {len(schedule)}")
        if len(schedule) > 0:
            print(f"Sample Block: {schedule[0]['course']} ({schedule[0]['start']} - {schedule[0]['end']}) Status: {schedule[0]['status']}")
            
            # Verify Status Logic
            # Pick a block, check status.
            # Since it's 'today', and likely auto-generated start times (10am etc), 
            # if current time is late (e.g. 21:00), morning blocks should be 'missed'.
            pass
    else:
        print(f"FAIL: GET /schedule error: {resp.text}")

    print("\n--- Testing GET /users/profile ---")
    p_resp = requests.get(f"{BASE_URL}/users/profile", headers=headers)
    if p_resp.status_code == 200:
        print(f"PASS: Profile Retrieved. XP: {p_resp.json()['xp_points']}")
    else:
        print(f"FAIL: Profile error: {p_resp.text}")
        
    print("\n--- Testing GET /resources/tips ---")
    t_resp = requests.get(f"{BASE_URL}/resources/tips")
    if t_resp.status_code == 200:
        print(f"PASS: Tips Retrieved. Keys: {list(t_resp.json().keys())[:3]}")
    else:
        print(f"FAIL: Tips error: {t_resp.text}")

if __name__ == "__main__":
    test_schedule()
