from app import create_app, db
from app.models.user import User
from app.services.inference_service import InferenceService

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='20221192@nileuniversity.edu.ng').first()
    if user:
        print("TRIGGERING SCHEDULE GENERATION FOR:", user.email)
        InferenceService.generate_week_schedule(user.id)
    else:
        print("USER NOT FOUND")
