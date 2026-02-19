from app import create_app, db
from app.models.user import User
from app.services.inference_service import InferenceService

# Initialize the Flask App Context
app = create_app()

def run_total_regeneration():
    with app.app_context():
        print("--- Starting Schedule Regeneration ---")
        
        # 1. Fetch all users to update their dashboards
        users = User.query.all()
        
        if not users:
            print("No users found in the database. Ensure your database is seeded.")
            return

        for user in users:
            print(f"Targeting User: {user.username} (ID: {user.id})")
            
            # 2. Trigger the new InferenceService logic
            # This method now handles internal ScheduleBlock deletion
            # and applies the 'Deep Work' vs 'Standard' slot logic.
            result = InferenceService.generate_week_schedule(user.id)
            
            print(f"Result for {user.username}: {result}")
            print("-" * 30)
            
        print("\nSUCCESS: All schedules have been synchronized with Africa/Lagos time.")
        print("Adaptive rules for Environment, Vibe, and Templates are now active.")

if __name__ == "__main__":
    run_total_regeneration()