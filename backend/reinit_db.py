import sys
import os
sys.path.append(os.getcwd())

from app import create_app, db
from app.models.session import ScheduleBlock
from sqlalchemy import text

app = create_app()


with app.app_context():
    # 1. Drop ScheduleBlock table to clear schema
    print("Dropping ScheduleBlock table...")
    try:
        ScheduleBlock.__table__.drop(db.engine)
        print("Dropped.")
    except Exception as e:
        print(f"Drop Skipped/Error: {e}")

    # 2. Re-create all tables (will create ScheduleBlock with new columns)
    print("Re-creating tables...")
    db.create_all()
    print("Database Schema Updated.")
