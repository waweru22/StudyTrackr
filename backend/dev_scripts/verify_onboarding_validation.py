from app import create_app, db
from app.services.auth_service import AuthService
from app.models.user import User

app = create_app()

def verify_onboarding_validation():
    print("--- Verifying Onboarding Validation ---")
    
    # 1. Test Password Mismatch
    bad_match_data = {
        'email': 'mismatch@test.com',
        'username': 'mismatch',
        'level': 100,
        'password': 'password123',
        'confirm_password': 'password1234',
        'learning_style': 'K'
    }
    user, msg = AuthService.register_user(bad_match_data)
    print(f"[Test 1] Mismatch: {msg}")
    assert user is None
    assert "not match" in msg
    
    # 2. Test Short Password
    short_pw_data = {
        'email': 'short@test.com',
        'username': 'short',
        'level': 100,
        'password': 'short',
        'confirm_password': 'short',
        'learning_style': 'K'
    }
    user, msg = AuthService.register_user(short_pw_data)
    print(f"[Test 2] Short PW: {msg}")
    assert user is None
    assert "at least 8" in msg
    
    # 3. Test Success
    good_data = {
        'email': 'good@test.com',
        'username': 'gooduser',
        'level': 100,
        'password': 'securepassword123',
        'confirm_password': 'securepassword123',
        'learning_style': 'K',
        'study_mode': 'SOLO',
        'focus_threshold': 60
    }
    # Clean up first
    existing = User.query.filter_by(email='good@test.com').first()
    if existing: 
        db.session.delete(existing)
        db.session.commit()
        
    user, msg = AuthService.register_user(good_data)
    print(f"[Test 3] Success: {msg}")
    assert user is not None
    assert msg == "Success"
    
    print("✅ Validation Logic Verified.")

if __name__ == '__main__':
    with app.app_context():
        verify_onboarding_validation()
