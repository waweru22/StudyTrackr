
from app import create_app, db
from app.models import Course

app = create_app()

def seed_courses():
    with app.app_context():
        # Clear existing courses to avoid duplicates if re-run (optional, but safer for fresh seed)
        # db.session.query(Course).delete()
        
        courses_data = [
            # Level 100
            {"code": "MTH 101", "title": "General Mathematics I", "level": 100, "weight": 3},
            {"code": "PHY 101", "title": "General Physics I", "level": 100, "weight": 3},
            {"code": "CHM 101", "title": "General Chemistry I", "level": 100, "weight": 3},
            {"code": "BIO 101", "title": "General Biology I", "level": 100, "weight": 3},
            {"code": "GST 101", "title": "Use of English I", "level": 100, "weight": 2},
            {"code": "CSC 101", "title": "Introduction to Computer Science", "level": 100, "weight": 3},

            # Level 200
            {"code": "CSC 201", "title": "Computer Programming I", "level": 200, "weight": 3},
            {"code": "CSC 203", "title": "Introduction to Digital Design", "level": 200, "weight": 2},
            {"code": "MTH 201", "title": "Mathematical Methods I", "level": 200, "weight": 3},
            {"code": "STA 201", "title": "Statistics for Physical Sciences", "level": 200, "weight": 2},
            {"code": "GST 201", "title": "Nigerian Peoples and Culture", "level": 200, "weight": 2},

            # Level 300
            {"code": "CSC 301", "title": "Structured Programming", "level": 300, "weight": 3},
            {"code": "CSC 305", "title": "Operating Systems I", "level": 300, "weight": 3},
            {"code": "CSC 309", "title": "Database Management Systems", "level": 300, "weight": 3},
            {"code": "CSC 311", "title": "Algorithms and Complexity Analysis", "level": 300, "weight": 3},
            {"code": "ENS 301", "title": "Entrepreneurial Studies I", "level": 300, "weight": 2},

            # Level 400
            {"code": "CSC 401", "title": "Organization of Programming Languages", "level": 400, "weight": 3},
            {"code": "CSC 403", "title": "Software Engineering", "level": 400, "weight": 3},
            {"code": "CSC 411", "title": "Artificial Intelligence", "level": 400, "weight": 3},
            {"code": "CSC 421", "title": "Net-Centric Computing", "level": 400, "weight": 3},
            {"code": "CSC 499", "title": "Project", "level": 400, "weight": 6},

            # Level 500
            {"code": "CSC 501", "title": "Advanced Software Engineering", "level": 500, "weight": 3},
            {"code": "CSC 503", "title": "Computer Networks II", "level": 500, "weight": 3},
            {"code": "CSC 599", "title": "Final Year Project", "level": 500, "weight": 8},
        ]

        print(f"Seeding {len(courses_data)} courses...")
        
        for c in courses_data:
            exists = Course.query.filter_by(code=c['code']).first()
            if not exists:
                new_course = Course(
                    code=c['code'],
                    name=c['title'], # Changed from title to name based on error
                    level=c['level'],
                    weight=c['weight']
                )
                db.session.add(new_course)
        
        db.session.commit()
        print("Courses seeded successfully!")

if __name__ == '__main__':
    seed_courses()
