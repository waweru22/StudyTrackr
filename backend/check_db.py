"""
StudyTrackr -- Database Connection & Seed Check
================================================
Run:  python check_db.py  (from backend/)

Verifies:
  1. DATABASE_URL is set
  2. Connection to the database works
  3. Seed data exists (courses, rules, users)
"""

import os
import sys

# Fix Windows console encoding for Unicode output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

db_url = os.environ.get("DATABASE_URL", "NOT SET")
if db_url == "NOT SET":
    print("[FAIL] DATABASE_URL is not set in .env")
    print("  Copy .env.example to .env and fill in your Supabase connection string.")
    sys.exit(1)

# Mask password for display
safe_url = db_url[:40] + "..." if len(db_url) > 40 else db_url
print(f"Database URL: {safe_url}")

try:
    from app import create_app, db
    app = create_app()

    with app.app_context():
        # Test connection
        db.session.execute(db.text("SELECT 1"))
        print("[OK] Database connection successful\n")

        from app.models.course import Course, StudyKnowledge
        from app.models.user import User
        from app.models.notification_trigger import NotificationTrigger

        counts = {
            "Courses": Course.query.count(),
            "Knowledge rules": StudyKnowledge.query.count(),
            "Notification triggers": NotificationTrigger.query.count(),
            "Users": User.query.count(),
        }

        print("--- Table Counts ---")
        for name, count in counts.items():
            status = "[OK]" if count > 0 else "[EMPTY]"
            print(f"  {status} {name}: {count}")

        ernest = User.query.filter_by(email='20221192@nileuniversity.edu.ng').first()
        ameer = User.query.filter_by(email='20220088@nileuniversity.edu.ng').first()
        print(f"  {'[OK]' if ernest else '[MISSING]'} Ernest (demo user)")
        print(f"  {'[OK]' if ameer else '[MISSING]'} Ameer (demo user)")

        all_seeded = all(c > 0 for c in counts.values())
        print()
        if all_seeded and ernest and ameer:
            print("[OK] Database is seeded and ready")
        elif all(c == 0 for c in counts.values()):
            print("[FAIL] Database appears empty -- ask the project lead to run the seeder")
        else:
            print("[WARN] Database is partially seeded -- ask the project lead to check")

except Exception as e:
    print(f"\n[FAIL] Connection failed: {e}")
    print("  Check your DATABASE_URL in .env and make sure the database is accessible.")
    sys.exit(1)
