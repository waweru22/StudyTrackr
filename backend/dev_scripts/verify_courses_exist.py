from app import create_app, db
from app.models.course import Course

app = create_app()

with app.app_context():
    count = Course.query.count()
    print(f"Total Courses in DB: {count}")
    
    if count > 0:
        print("Sample Courses:")
        courses = Course.query.limit(5).all()
        for c in courses:
            print(f"- {c.code} ({c.name}) Level: {c.level} Sem: {c.semester}")
    else:
        print("WARNING: Course table is empty! You may need to run the seeder.")
