from app import create_app
from flask import json

app = create_app()

def verify_all_courses():
    print("--- Verifying GET /courses/all ---")
    
    with app.test_client() as client:
        res = client.get('/courses/all')
        print(f"Status: {res.status_code}")
        assert res.status_code == 200
        
        data = res.get_json()
        print(f"Total Courses: {len(data)}")
        
        if not data:
            print("No courses found.")
            return

        print("\nFirst 5 Courses (Sorted by Level, Code):")
        for i, c in enumerate(data[:5]):
            print(f"{i+1}. [L{c['level']}] {c['code']} - {c['name']} (ID: {c['id']}, W: {c['weight']})")
            
        # Check sorting
        first = data[0]
        last = data[-1]
        print(f"\nFirst: {first['code']} (Level {first['level']})")
        print(f"Last: {last['code']} (Level {last['level']})")
        
        if len(data) > 1:
            assert data[0]['level'] <= data[1]['level']

    print("\n✅ Verification Complete.")

if __name__ == '__main__':
    verify_all_courses()
