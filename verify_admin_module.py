import requests
import json
import time

BASE_URL = 'http://localhost:5000'
ADMIN_EMAIL = f'admin_test_{int(time.time())}@nileuni.edu.ng'
ADMIN_PW = 'admin123'
STUDENT_EMAIL = 'student_test@example.com' 
STUDENT_PW = 'password123'

def register_admin():
    print(f"Registering Admin: {ADMIN_EMAIL}")
    res = requests.post(f"{BASE_URL}/auth/admin/register", json={
        'username': 'AdminUser',
        'email': ADMIN_EMAIL,
        'password': ADMIN_PW,
        'confirm_password': ADMIN_PW,
        'staff_id': 'STAFF001'
    })
    
    if res.status_code == 201:
        print("Admin Registration Init (OTP Sent)")
        otp = res.json().get('otp_debug')
        verify = requests.post(f"{BASE_URL}/auth/verify-otp", json={
            'email': ADMIN_EMAIL, 'otp_code': otp
        })
        print(f"Verify Status: {verify.status_code}")
        try:
             return verify.json().get('access_token')
        except:
             print(f"Verify Failed Body: {verify.text}")
             return None
    elif "already registered" in res.text:
        print("Admin exists, logging in")
        # Just use login? No, verification script uses OTP flow.
        otp_res = requests.post(f"{BASE_URL}/auth/request-otp", json={'email': ADMIN_EMAIL})
        if otp_res.status_code != 200:
             print(f"OTP Request Failed: {otp_res.text}")
             return None
        otp = otp_res.json().get('otp_debug')
        print(f"Got OTP: {otp}")
        try:
            print("Verifying OTP...")
            verify = requests.post(f"{BASE_URL}/auth/verify-otp", json={
                'email': ADMIN_EMAIL, 'otp_code': otp
            })
            print(f"Verify Status: {verify.status_code}")
            resp_json = verify.json()
            print(f"Verify Response: {resp_json}")
            if verify.status_code == 200:
                 token = resp_json.get('access_token')
                 print(f"Token retrieved: {token}")
                 return token
            else:
                 print(f"Login Verification Failed: {verify.text}")
                 return None
        except Exception as e:
            print(f"Verify Exception: {e}")
            return None
    else:
        print(f"Admin Reg Failed: {res.text}")
        return None

def register_student():
    # Helper to get student token
    try:
        res = requests.post(f"{BASE_URL}/auth/onboard", json={
            'username': 'StudentUser',
            'email': STUDENT_EMAIL,
            'password': STUDENT_PW,
            'confirm_password': STUDENT_PW,
            'level': 'Undergraduate',
            'selected_course_ids': [1]
        })
        if res.status_code == 201:
            return res.json().get('access_token')
        
        otp_res = requests.post(f"{BASE_URL}/auth/request-otp", json={'email': STUDENT_EMAIL})
        otp_code = otp_res.json().get('otp_debug')
        verify_res = requests.post(f"{BASE_URL}/auth/verify-otp", json={
            'email': STUDENT_EMAIL, 'otp_code': otp_code
        })
        return verify_res.json().get('access_token')
    except Exception as e:
        print(f"Student Reg Exception: {e}")
        return None

def test_admin_module():
    print("Testing Faculty Administrator Module...")
    
    admin_token = register_admin()
    if not admin_token: return
    
    print(f"Admin Token: {admin_token[:10]}...")
    
    student_token = register_student()
    if not student_token:
         print("Failed to get student token")
         return
         
    print(f"Student Token: {student_token[:10]}...")
    print(f"Student Token: {student_token[:10]}...")
    
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    student_headers = {'Authorization': f'Bearer {student_token}'}
    
    print("\n[Test 1] Create Course (Admin)")
    res = requests.post(f"{BASE_URL}/courses/", json={
        'code': 'CMP404', 'name': 'Advanced AI', 'level': 400, 'weight': 3
    }, headers=admin_headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 201:
        course_id = res.json().get('id')
        print(f"PASS: Course created ID {course_id}")
    else:
        print(f"FAIL: {res.text}")
        course_id = None
        
    print("\n[Test 2] Create Course (Student should fail)")
    res = requests.post(f"{BASE_URL}/courses/", json={
        'code': 'HACK101', 'name': 'Hacking', 'level': 100
    }, headers=student_headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 403:
        print("PASS: Student access denied")
    else:
        print(f"FAIL: Student access allowed {res.status_code}")

    print("\n[Test 3] Create Broadcast")
    res = requests.post(f"{BASE_URL}/admin/broadcast", json={
        'message': 'Test Broadcast', 'target_level': 400
    }, headers=admin_headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 201:
        print("PASS: Broadcast sent")
    else:
        print(f"FAIL: {res.text}")
        
    print("\n[Test 4] Analytics Focus")
    res = requests.get(f"{BASE_URL}/admin/analytics/focus", headers=admin_headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Data: {res.json()[:2]}") # Show first 2
        print("PASS: Analytics Retrieved")
    else:
        print(f"FAIL: {res.text}")

    # Cleanup optional
    if course_id:
        requests.delete(f"{BASE_URL}/courses/{course_id}", headers=admin_headers)

if __name__ == "__main__":
    test_admin_module()
