from app import create_app
from flask import json

app = create_app()

def verify_users():
    print("--- Verifying GET /users/ ---")
    
    with app.test_client() as client:
        res = client.get('/users/')
        print(f"Status: {res.status_code}")
        assert res.status_code == 200
        
        data = res.get_json()
        print(f"Total Users: {len(data)}")
        
        if not data:
            print("No users found.")
            return

        print("\nLatest User:")
        user = data[0]
        print(f"ID: {user['id']} | Username: {user['username']}")
        print(f"Profile: {user['base_template']} | Peak: {user['peak_time']}")
        print(f"Stats: {user['xp_points']} XP | Badge: {user['badge']}")
        
        # Check required fields
        expected = ['focus_threshold', 'daily_cognitive_budget', 'email', 'level']
        for k in expected:
            assert k in user
            
        # Check Sorting
        if len(data) > 1:
            print(f"Second User ID: {data[1]['id']}")
            assert user['id'] > data[1]['id']

    print("\n✅ Verification Complete.")

if __name__ == '__main__':
    verify_users()
