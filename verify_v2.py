from app import create_app, db
from app.models.user import User
from app.models.note import Note
from app.utils.constants import TECHNIQUE_INSTRUCTIONS

app = create_app()

with app.app_context():
    print("Verifying Models...")
    # Check if we can query Note (even if empty)
    notes = Note.query.all()
    print("Note model accessible.")
    
    print("Verifying Constants...")
    assert "Pomodoro" in TECHNIQUE_INSTRUCTIONS
    print("Constants loaded.")
    
    print("Verifying Blueprints...")
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert any('/notes/' in r for r in rules)
    assert any('/resources/search' in r for r in rules)
    assert any('/audit/run' in r for r in rules)
    print("Routes registered.")
    
    print("Verification Passed.")
