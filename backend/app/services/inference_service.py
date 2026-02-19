from datetime import datetime, timedelta, time, timezone
from app import db
from app.models.session import ScheduleBlock
from app.models.course import Course
from app.services.rule_engine import RuleEngine
import random

class InferenceService:
    @staticmethod
    def generate_week_schedule(user_id, selected_course_ids=None):
        from app.models.user import User
        LAGOS_TZ = timezone(timedelta(hours=1))
        
        user = User.query.get(user_id)
        if not user: return "User not found."

        # 1. FETCH CONTEXT & FIX COLD START
        user_context_base = RuleEngine.get_user_context(user_id)
        # Standardize template name to match seeder (Case-insensitive check)
        raw_template = str(user.base_template or "Standard").lower()
        
        # 2. ALIGN WITH CALENDAR GRID (Start from Monday)
        # This fixes the "empty Mon-Wed" issue
        today = datetime.now(LAGOS_TZ).date()
        start_of_week = today - timedelta(days=today.weekday()) # Force to Monday
        
        all_courses = user.courses if not selected_course_ids else Course.query.filter(Course.id.in_(selected_course_ids)).all()
        if not all_courses: return "No courses found."
        
        db.session.query(ScheduleBlock).filter_by(user_id=user.id).delete()
        
        # 3. ROTATIONAL QUEUE
        ranked_courses = sorted([{'course': c, 'score': c.weight * c.credits, 'id': c.id} for c in all_courses], key=lambda x: x['score'], reverse=True)
        random.shuffle(ranked_courses)
        course_queue = ranked_courses[:]

        # 4. GENERATION LOOP (Mon-Sun)
        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            day_name = current_day.strftime("%A")
            used_today_ids = []

            # 3 Slots with 4h Spacing
            start_hour_map = {'morning': 8, 'afternoon': 13, 'night': 18}
            base_peak = start_hour_map.get(str(user.peak_time).lower(), 9)
            slot_hours = [base_peak, (base_peak + 4) % 24, (base_peak + 8) % 24]

            for hour in slot_hours:
                if not course_queue: course_queue = ranked_courses[:]
                selected = next((c for c in course_queue if c['id'] not in used_today_ids), course_queue[0])
                c_obj = selected['course']
                used_today_ids.append(c_obj.id)
                course_queue.remove(selected)

                # DURATION LOGIC (Active Recall = 45m, Deep Work = 120m)
                duration = 60
                if 'deep' in raw_template and c_obj.weight >= 4: duration = 120
                elif 'recall' in raw_template: duration = 45
                elif 'pomodoro' in raw_template: duration = 25

                # EXPERT SYSTEM REFINEMENT
                pred_ctx = RuleEngine.get_predictive_context(user_id, day_name, hour)
                rule_context = user_context_base.copy()
                rule_context.update({'course_weight': c_obj.weight, 'session_vibe': pred_ctx.get('session_vibe')})
                
                matched_rules = RuleEngine.evaluate_triggers(rule_context)
                
                # Default Technique if Active Recall template is active
                tech_name = "Active Recall (Blurting)" if 'recall' in raw_template else "Standard Session"
                tech_details = "Write everything you know from memory, then check notes." if 'recall' in raw_template else "Focus on core concepts."

                for rule in matched_rules:
                    tech_name, tech_details = rule.principle, rule.content

                # SAVE BLOCK
                start_dt = datetime.combine(current_day, time(hour, 0))
                db.session.add(ScheduleBlock(
                    user_id=user.id, date=current_day, day_of_week=day_name,
                    start_time=start_dt.time(), 
                    end_time=(start_dt + timedelta(minutes=duration)).time(),
                    block_type="Deep Work" if duration >= 90 else "Lecture",
                    status="upcoming", technique_name=tech_name, technique_details=tech_details,
                    course_id=c_obj.id
                ))

        db.session.commit()
        return "V6 Adaptive Schedule Generated"