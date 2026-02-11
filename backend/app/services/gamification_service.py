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
    def penalize_missed_session(user_id):
        user = User.query.get(user_id)
        if not user: return 0
        
        penalty_amount = 50 # Fixed penalty for missed session
        
        # Deduct, but don't go below 0 for now (or maybe allow negative? let's stick to 0 floor)
        user.xp_points = max(0, user.xp_points - penalty_amount)
        
        db.session.commit()
        return penalty_amount

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

    @staticmethod
    def calculate_streak(user_id):
        """
        Checks if the difference between current time and last completed ScheduleBlock.created_at
        is less than 24 hours to maintain the user's daily streak.
        """
        from app.models.session import ScheduleBlock
        from datetime import datetime, timedelta
        
        user = User.query.get(user_id)
        if not user: return
        
        last_block = ScheduleBlock.query.filter_by(user_id=user_id).order_by(ScheduleBlock.created_at.desc()).first()
        
        if not last_block:
            user.streak_count = 0
            db.session.commit()
            return
            
        now = datetime.utcnow()
        diff = now - last_block.created_at
        
        # Strict 24h check per requirements
        if diff > timedelta(hours=24):
            user.streak_count = 0
        else:
            # If within 24h, streak is maintained.
            # Ideally we increment if it's a "new day" action, but prompt just says "maintain".
            # We assume update_streak handles incrementing on action.
            pass
            
        db.session.commit()
