import sys
import os

# Ensure backend directory is in path
sys.path.append(os.getcwd())

from app import create_app
from app.models.user import User

app = create_app()

def check_users():
    print("--- Checking Users ---")
    with app.app_context():
        count = User.query.count()
        print(f"User Count: {count}")
        users = User.query.all()
        for u in users:
            print(f"User: {u.email} (ID: {u.id})")

if __name__ == "__main__":
    check_users()
