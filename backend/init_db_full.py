import sys
import os

# Ensure backend directory is in path
sys.path.append(os.getcwd())

from app import create_app, db
from app.utils.seeder import seed_courses

app = create_app()

def init_db():
    print("--- Initializing Database ---")
    with app.app_context():
        # 1. Create Tables
        print("Dropping all tables...")
        db.drop_all()
        print("Creating tables...")
        db.create_all()
        print("Tables created.")
        
        # 2. Seed Data
        print("Seeding courses and knowledge...")
        seed_courses()
        print("Seeding complete.")

if __name__ == "__main__":
    init_db()
