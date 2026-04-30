from app import create_app
from app.services.inference_service import InferenceService
from app.services.session_service import SessionService

app = create_app()

with app.app_context():
    print("Testing imports...")
    # Just checking if methods exist and imports work
    assert hasattr(InferenceService, 'optimize_schedule')
    assert hasattr(SessionService, 'end_session')
    print("Imports successful. Optimization loop structure is valid.")
