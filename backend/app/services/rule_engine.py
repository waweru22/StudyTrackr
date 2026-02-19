from app import db
from app.models.course import StudyKnowledge
from app.models.session import StudySession, ScheduleBlock
from sqlalchemy import func
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RuleEngine")

class RuleEngine:
    @staticmethod
    def evaluate_triggers(context_data):
        """
        Dynamically parses 'inference_trigger' strings against context_data.
        """
        rules = StudyKnowledge.query.all()
        applicable_rules = []
        
        # Normalize context keys to lowercase for matching
        norm_context = {k.lower(): v for k, v in context_data.items()}
        
        for rule in rules:
            stmt = rule.inference_trigger.lower()
            if not stmt: continue
            
            is_match = False
            
            # Dynamic Parsing for Strings, Numbers, and Boolean Flags
            for key, val in norm_context.items():
                if key in stmt:
                    # 1. String Matching (Vibe, Learning Style, etc.)
                    if isinstance(val, str):
                        if f"'{val.lower()}'" in stmt or f'"{val.lower()}"' in stmt:
                            is_match = True
                    
                    # 2. Boolean Flags (e.g., is_peak_focus)
                    elif isinstance(val, bool):
                        if val is True and "true" in stmt: is_match = True
                        elif val is False and "false" in stmt: is_match = True

                    # 3. Numeric Comparisons
                    elif isinstance(val, (int, float)):
                        try:
                            if ">=" in stmt:
                                threshold = float(stmt.split(">=")[1].split()[0].replace(',', '').replace(';', ''))
                                if val >= threshold: is_match = True
                            elif "<=" in stmt:
                                threshold = float(stmt.split("<=")[1].split()[0].replace(',', '').replace(';', ''))
                                if val <= threshold: is_match = True
                        except (ValueError, IndexError):
                            continue

            if is_match:
                logger.info(f"[EXPERT SYSTEM] Rule Fired: {rule.principle}")
                applicable_rules.append(rule)
                
        return applicable_rules

    @staticmethod
    def get_predictive_context(user_id, day_of_week, start_hour):
        """
        Solves the Cold Start problem and provides predictive energy mapping.
        """
        from app.models.user import User
        user = User.query.get(user_id)
        
        # 1. Check for History (Mature Phase)
        # Search for sessions on this weekday within a +/- 1 hour window
        historical_sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            func.strftime('%w', StudySession.start_time) == RuleEngine._get_day_int(day_of_week),
            func.cast(func.strftime('%H', StudySession.start_time), db.Integer).between(start_hour - 1, start_hour + 1)
        ).all()

        # 2. Logic: Cold Start vs. Mature
        if len(historical_sessions) < 5:
            # --- COLD START FALLBACK ---
            is_peak = False
            peak_t = str(user.peak_time or '').lower()
            if 'morning' in peak_t and 8 <= start_hour <= 12: is_peak = True
            elif 'afternoon' in peak_t and 13 <= start_hour <= 17: is_peak = True
            elif ('evening' in peak_t or 'night' in peak_t) and 18 <= start_hour <= 22: is_peak = True

            return {
                'session_vibe': 'Normal',
                'avg_success_score': 1.0,
                'is_peak_focus': is_peak,
                'learning_style': user.learning_style,
                'is_cold_start': True
            }
        
        # --- MATURE PREDICTIVE LOGIC ---
        vibes = [s.vibe for s in historical_sessions if s.vibe]
        pred_vibe = max(set(vibes), key=vibes.count) if vibes else 'Normal'
        avg_score = sum(s.success_score for s in historical_sessions) / len(historical_sessions)

        return {
            'session_vibe': pred_vibe,
            'avg_success_score': avg_score,
            'is_peak_focus': (pred_vibe != 'Low Energy'),
            'learning_style': user.learning_style,
            'is_cold_start': False
        }

    @staticmethod
    def _get_day_int(day_name):
        days = {"Sunday": "0", "Monday": "1", "Tuesday": "2", "Wednesday": "3", "Thursday": "4", "Friday": "5", "Saturday": "6"}
        return days.get(day_name, "1")

    @staticmethod
    def get_user_context(user_id):
        from app.models.user import User
        from app.models.session import StudySession, ScheduleBlock
        from sqlalchemy import func
        
        user = User.query.get(user_id)
        if not user: return {}

        # 1. Base Profile Context
        context = {
            'user_level': user.level,
            'learning_style': user.learning_style,
            'peak_time': user.peak_time,
            'base_template': user.base_template,
            'focus_threshold': user.focus_threshold,
            'daily_cognitive_budget': user.daily_cognitive_budget,
            'streak_count': user.streak_count
        }

        # 2. Aggregated Session History (Real Data)
        # Calculate consistency of location/time
        total_sessions = StudySession.query.filter_by(user_id=user_id).count() or 1
        
        # Avg Success Score
        avg_score = db.session.query(func.avg(StudySession.success_score)).filter_by(user_id=user_id).scalar() or 0.0
        context['avg_session_efficacy'] = float(avg_score)

        # Environment Consistency (e.g. % of sessions in "Library")
        # For simplicity, we just check if they have a dominant location
        top_env = db.session.query(StudySession.environment, func.count(StudySession.environment)).filter_by(user_id=user_id).group_by(StudySession.environment).order_by(func.count(StudySession.environment).desc()).first()
        if top_env:
            context['session_location_consistency'] = top_env[1] / total_sessions
            context['dominant_environment'] = top_env[0]
        else:
            context['session_location_consistency'] = 0.0
            context['dominant_environment'] = "None"

        # Vibe Checks
        recent_vibes = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.start_time.desc()).limit(3).all()
        # If 2/3 recent sessions were "Low Energy", flag burnout risk
        low_energy_count = sum(1 for s in recent_vibes if s.vibe == 'Low Energy')
        context['burnout_risk'] = 'High' if low_energy_count >= 2 else 'Low'

        # Cumulative Minutes (for Interleaving triggers)
        # This is usually per-course, but we can store global for general rules
        # Specific course logic happens in the loop
        
        return context