from app import create_app,db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='wawerulearns_').first()
    if user:
        print(f"User found: {user.username} (ID: {user.id})")
        print("Selected Courses:")
        if user.courses:
            for course in user.courses:
                print(f"- {course.code}: {course.name} (Level {course.level})")
        else:
            print("No courses selected.")
    else:
        print("User 'wawerulearns_' not found.")
        print("Listing all users:")
        users = User.query.all()
        for u in users:
            print(f"- {u.username}")
