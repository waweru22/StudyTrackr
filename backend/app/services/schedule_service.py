from app import db
from app.models.session import ScheduleBlock, StudySession
from app.models.notification import Notification
from datetime import datetime, timedelta

class ScheduleService:
    @staticmethod
    def check_missed_sessions(user_id):
        # Trigger: Current time > start_time + 15 mins
        now = datetime.utcnow()
        today_date = now.date()
        
        blocks = ScheduleBlock.query.filter_by(user_id=user_id, date=today_date).all()
        
        notifications_created = 0
        
        for block in blocks:
            # Combine to DateTime
            block_start_dt = datetime.combine(block.date, block.start_time)
            missed_threshold = block_start_dt + timedelta(minutes=15)
            
            if now > missed_threshold:
                start_of_day = datetime.combine(today_date, datetime.min.time())
                end_of_day = datetime.combine(today_date, datetime.max.time())
                
                session_exists = StudySession.query.filter_by(
                    user_id=user_id, 
                    course_id=block.course_id
                ).filter(
                    StudySession.start_time >= start_of_day,
                    StudySession.start_time <= end_of_day
                ).first()
                
                if not session_exists:
                    course_name = block.course.code if block.course else "General Block"
                    msg = f"You missed your {course_name} block today at {block.start_time.strftime('%H:%M')}. It has been noted."
                    
                    # Dedup check against Notification table
                    existing = Notification.query.filter_by(
                        user_id=user_id,
                        message=msg
                    ).first()
                    
                    if not existing:
                        # Write to Notification (single source of truth)
                        from app.services.notification_service import NotificationService
                        NotificationService.create_notification(
                            user_id=user_id,
                            title="Missed session",
                            message=msg,
                            type="alert"
                        )
                        notifications_created += 1
                        
                        # Apply Penalty
                        from app.services.gamification_service import GamificationService
                        GamificationService.penalize_missed_session(user_id)
                        
        return notifications_created > 0
