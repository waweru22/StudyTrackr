from app import db
from app.models.session import ScheduleBlock, StudySession
from app.models.system_alert import SystemAlert
from datetime import datetime, timedelta

class ScheduleService:
    @staticmethod
    def check_missed_sessions(user_id):
        # Trigger: Current time > start_time + 15 mins
        now = datetime.utcnow()
        today_date = now.date()
        current_time_val = now.time()
        
        # 1. Get Today's ScheduleBlocks
        # We need to check blocks that have ALREADY started at least 15 mins ago
        # Condition: block.start_time < (current_time - 15 mins)
        # Time arithmetic can be tricky with just 'time' objects. safer to combine.
        
        blocks = ScheduleBlock.query.filter_by(user_id=user_id, date=today_date).all()
        
        alerts_created = 0
        
        for block in blocks:
            # Combine to DateTime
            block_start_dt = datetime.combine(block.date, block.start_time)
            missed_threshold = block_start_dt + timedelta(minutes=15)
            
            # Check if we are past the threshold
            if now > missed_threshold:
                # 2. Check if a StudySession exists for this block
                # Assumption: StudySession created within window?
                # Or simply: check if ANY session was started for this course today?
                # "You missed your [Course] block."
                # Let's check if there is a StudySession for this course created today?
                # This is loose, but covers "did they study?".
                # Stricter: Did they study near the time?
                # Let's use loose check: Did they study this course today?
                
                # Check if session exists for this course on this day
                # We need to check datetime range of 'today'
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
                    # 3. Check if we already alerted this specific block?
                    # Avoid spam.
                    # Unique Message: "Missed Session: {CourseName} on {Date}"
                    course_name = block.course.code if block.course else "General Block"
                    msg = f"You missed your {course_name} block today at {block.start_time}. Schedule re-optimized."
                    
                    existing_alert = SystemAlert.query.filter_by(
                        user_id=user_id,
                        message=msg
                    ).first()
                    
                    if not existing_alert:
                        # Create Alert
                        alert = SystemAlert(
                            user_id=user_id,
                            message=msg
                        )
                        db.session.add(alert)
                        alerts_created += 1
                        
        if alerts_created > 0:
            db.session.commit()
            return True
            
        return False
