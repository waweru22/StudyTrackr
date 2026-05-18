"""Update demo users to is_verified=True so they are not locked out."""
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    result = db.session.execute(
        db.text("""
            UPDATE "user" SET is_verified = TRUE 
            WHERE email IN (
                '20221192@nileuniversity.edu.ng',
                '20220088@nileuniversity.edu.ng'
            )
        """)
    )
    db.session.commit()
    
    # Verify
    ernest = User.query.filter_by(email='20221192@nileuniversity.edu.ng').first()
    ameer = User.query.filter_by(email='20220088@nileuniversity.edu.ng').first()
    
    print(f"Ernest is_verified: {ernest.is_verified if ernest else 'NOT FOUND'}")
    print(f"Ameer  is_verified: {ameer.is_verified if ameer else 'NOT FOUND'}")
    print(f"Rows affected: {result.rowcount}")
