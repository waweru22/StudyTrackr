from app import create_app, db
from app.models.course import Material
import os

app = create_app()

def clear_materials():
    with app.app_context():
        num_deleted = db.session.query(Material).delete()
        db.session.commit()
        print(f"✅ Successfully deleted {num_deleted} records from the 'materials' table.")

if __name__ == "__main__":
    clear_materials()
