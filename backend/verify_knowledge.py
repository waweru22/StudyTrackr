from app import create_app, db
from app.models.course import StudyKnowledge

app = create_app()

with app.app_context():
    count = StudyKnowledge.query.count()
    print(f"Total Knowledge Rules: {count}")
    if count > 0:
        rules = StudyKnowledge.query.limit(5).all()
        for r in rules:
            print(f"- {r.principle} (Tags: {r.tags})")
