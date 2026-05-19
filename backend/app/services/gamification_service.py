from app import db
from app.models.user import User

class GamificationService:
    @staticmethod
    def award_xp(user_id, net_duration_minutes, distraction_count=0):
        user = User.query.get(user_id)
        if not user: return 0

        # Accept a StudySession object as the second arg (seed script compat)
        if hasattr(net_duration_minutes, 'duration_minutes'):
            session = net_duration_minutes
            net_duration_minutes = session.duration_minutes or 0
        
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
        
        penalty_amount = 50
        user.xp_points = max(0, user.xp_points - penalty_amount)
        
        db.session.commit()
        return penalty_amount

    @staticmethod
    def check_badges(user):
        if user.xp_points >= 1000 and user.badge == "Novice":
            user.badge = "Apprentice"
        elif user.xp_points >= 5000 and user.badge == "Apprentice":
            user.badge = "Master"
        elif user.xp_points >= 10000:
            user.badge = "Grandmaster"

    @staticmethod
    def calculate_streak(user_id):
        """
        Recalculates streak based on fully completed StudySessions.
        A day only counts toward the streak if the user has at least one
        session with completed_on_time=True on that day.
        Streak increments only once per calendar day.
        """
        from app.models.session import StudySession
        from datetime import datetime, date, timedelta

        user = User.query.get(user_id)
        if not user:
            return

        today = date.today()
        yesterday = today - timedelta(days=1)

        # Only sessions that were fully completed count toward the streak
        completed_sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.end_time != None,
            StudySession.completed_on_time == True
        ).order_by(StudySession.start_time.desc()).all()

        if not completed_sessions:
            user.streak_count = 0
            db.session.commit()
            return

        # Build a set of unique dates with fully completed sessions
        completed_dates = sorted(
            set(s.start_time.date() for s in completed_sessions),
            reverse=True
        )

        # Check if streak is still active (most recent completed day is today or yesterday)
        if completed_dates[0] < yesterday:
            user.streak_count = 0
            db.session.commit()
            return

        # Count consecutive days backwards from today
        streak = 0
        check_date = today if completed_dates[0] == today else yesterday

        for d in completed_dates:
            if d == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            elif d < check_date:
                break

        user.streak_count = streak
        db.session.commit()
