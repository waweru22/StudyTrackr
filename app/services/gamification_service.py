from app import db
from app.models.user import User

class GamificationService:
    @staticmethod
    @staticmethod
    def award_xp(user_id, net_duration_minutes, distraction_count):
        user = User.query.get(user_id)
        if not user: return 0
        
        # Base XP: 90m = 100 XP (Calculated from Net Duration)
        base_xp = (net_duration_minutes / 90.0) * 100.0
        
        # Penalty: 10 XP per distraction
        penalty = distraction_count * 10.0
        
        # Final XP: Base - Penalty, floored at 0
        final_xp = int(max(0, base_xp - penalty))
        
        user.xp_points += final_xp
        
        # Update Badges
        GamificationService.check_badges(user)
        
        db.session.commit()
        return final_xp

    @staticmethod
    def check_badges(user):
        # Simple thresholds
        if user.xp_points >= 1000 and user.badge == "Novice":
            user.badge = "Apprentice"
        elif user.xp_points >= 5000 and user.badge == "Apprentice":
            user.badge = "Master"
        elif user.xp_points >= 10000:
            user.badge = "Grandmaster"
            
    @staticmethod
    def update_streak(user_id):
        user = User.query.get(user_id)
        # Logic to check if practiced yesterday would go here
        # For simplicity, just increment
        user.streak_count += 1
        db.session.commit()
