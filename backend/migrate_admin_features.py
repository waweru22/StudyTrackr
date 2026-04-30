"""
Migration script for Admin Interface features.
Adds: is_verified (User), is_active (Course), admin_broadcast table.
Safe to run multiple times (catches 'column already exists' errors).
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        engine = db.engine
        with engine.connect() as conn:
            # 1. Add is_verified to User (default TRUE for existing students)
            try:
                conn.execute(text("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 1"))
                conn.commit()
                print("[OK] Added 'is_verified' column (existing users default to verified).")
            except Exception as e:
                print(f"[SKIP] is_verified: {e}")

            # 2. Add is_active to Course (default TRUE)
            try:
                conn.execute(text("ALTER TABLE course ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                conn.commit()
                print("[OK] Added 'is_active' column to course.")
            except Exception as e:
                print(f"[SKIP] is_active: {e}")

        # 3. Create admin_broadcast table (via model)
        db.create_all()
        print("[OK] Ensured admin_broadcast table exists (create_all).")

    print("\nMigration complete.")

if __name__ == "__main__":
    migrate()
