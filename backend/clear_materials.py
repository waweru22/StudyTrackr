from app import create_app, db
from app.models.course import SavedResource
import os

app = create_app()

def clear_saved_resources():
    with app.app_context():
        num_deleted = db.session.query(SavedResource).delete()
        db.session.commit()
        print(f"✅ Successfully deleted {num_deleted} records from the 'saved_resource' table.")

if __name__ == "__main__":
    clear_saved_resources()
