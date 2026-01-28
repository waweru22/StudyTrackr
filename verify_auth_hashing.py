from app import create_app, db
from app.models.user import User
from app.services.auth_service import AuthService
from werkzeug.security import check_password_hash

app = create_app()

def verify_hashing():
    print("--- Verifying Password Hashing ---")
    
    email = "hash_test@example.com"
    password = "SafePassword123!"
    
    # Cleanup
    with app.app_context():
        User.query.filter_by(email=email).delete()
        db.session.commit()
    
        # Register
        data = {
            'email': email,
            'username': 'HashTester',
            'level': 100,
            'password': password,
            'confirm_password': password,
            'learning_style': 'V'
        }
        
        user, msg = AuthService.register_user(data)
        
        if not user:
            print(f"Registration Failed: {msg}")
            return
            
        print(f"User Created: {user.id}")
        
        # Verify DB content
        db_user = User.query.get(user.id)
        stored_hash = db_user.hashed_password
        
        print(f"Stored Hash: {stored_hash}")
        
        if stored_hash == password:
            print("❌ FAILURE: Password stored in plain text!")
        elif check_password_hash(stored_hash, password):
            print("✅ SUCCESS: Password hashed correctly and verified.")
        else:
            print("❌ FAILURE: Hash verification failed.")

if __name__ == '__main__':
    verify_hashing()
