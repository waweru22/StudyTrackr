from app import create_app, db
from sqlalchemy import text
from app.models.system_alert import SystemAlert # Ensure model is registered pattern

app = create_app()

def update_schema():
    with app.app_context():
        engine = db.engine
        with engine.connect() as conn:
            # Check if columns exist
            try:
                 # SQLite specific check or just try adding
                conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'student'"))
                print("Added 'role' column.")
            except Exception as e:
                print(f"Role column may exist: {e}")

            try:
                conn.execute(text("ALTER TABLE user ADD COLUMN staff_id VARCHAR(50)"))
                print("Added 'staff_id' column.")
            except Exception as e:
                print(f"Staff_id column may exist: {e}")
                
            # Create Broadcast table
            # Since we defined the model, we can try create_all for just that valid table if not exists?
            # Or assume migrate handles it?
            # create_all will create tables that don't exist.
            db.create_all()
            print("Database updated (Create All run for Broadcast).")

if __name__ == "__main__":
    update_schema()
