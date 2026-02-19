from app import create_app, db
from app.models.course import Material

app = create_app()

with app.app_context():
    print("Creating missing tables...")
    db.create_all()
    print("Tables created (if they didn't exist).")
