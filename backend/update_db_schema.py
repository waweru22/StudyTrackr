from app import create_app, db
from sqlalchemy import text
import sqlite3
import os

app = create_app()

def update_schema():
    with app.app_context():
        # Path to DB
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print(f"Connecting to database at: {db_path}")
        
        if not os.path.exists(db_path):
            print("Database not found, creating all tables...")
            db.create_all()
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Check if 'note' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='note';")
        if not cursor.fetchone():
            print("Table 'note' does not exist. Creating it via SQLAlchemy...")
            db.create_all()
            # If create_all created it, we are done (it uses latest model)
            print("Tables created.")
        else:
            print("Table 'note' exists. Checking columns...")
            # 2. Check columns
            cursor.execute("PRAGMA table_info(note);")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'file_path' not in columns:
                print("Adding 'file_path' column...")
                cursor.execute("ALTER TABLE note ADD COLUMN file_path VARCHAR(300);")
                
            if 'file_type' not in columns:
                print("Adding 'file_type' column...")
                cursor.execute("ALTER TABLE note ADD COLUMN file_type VARCHAR(20);")
                
            conn.commit()
            print("Schema updated successfully.")
            
        conn.close()

if __name__ == "__main__":
    update_schema()
