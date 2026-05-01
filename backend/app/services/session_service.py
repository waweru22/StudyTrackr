from app import db
from app.models.session import StudySession
from datetime import datetime, timedelta
from app.services.gamification_service import GamificationService
from app.services.notification_service import NotificationService


def generate_session_insight(session):
    parts = []
    env = session.environment or "unknown location"
    score = int(session.success_score or 0)
    vibe = session.vibe or ""
    mood_labels = {1: "Drained", 2: "Neutral", 3: "Energized"}
    mood = mood_labels.get(session.mood_after, "")

    if score >= 4 and vibe == "High Energy":
        parts.append(f"{score}/5 in the {env} with High Energy — your best conditions.")
    elif score <= 2 and session.distraction_count >= 2:
        parts.append(f"High distractions at {env} pulled this score down to {score}/5.")
    elif score <= 2 and vibe == "Low Energy":
        parts.append(f"Low energy session — {score}/5. The system will adjust tomorrow's load.")
    elif session.would_repeat is False:
        parts.append(f"You wouldn't repeat this technique. That's been noted for schedule refinement.")
    else:
        parts.append(f"{score}/5 — a solid session at {env}.")

    if mood:
        parts.append(f"You felt {mood} afterwards.")

    return " ".join(parts)


class SessionService:
    @staticmethod
    def start_session(user_id, data):
        new_session = StudySession(
            user_id=user_id,
            course_id=data['course_id'],
            session_goal=data.get('session_goal'),
            vibe=data.get('vibe'),
            social_setting=data.get('social_setting'),
            learning_mode=data.get('learning_mode'),
            medium=data.get('medium'),
            environment=data.get('environment'),
            start_time=datetime.utcnow()
        )
        
        # Zeigarnik Effect Nudge
        nudge = None
        if new_session.vibe == 'Low Energy':
            nudge = "Feeling low energy? Try working for just 10 minutes. Taking a tactical break might help!"
            
        # Dynamic Timer Logic
        from app.utils.constants import TECHNIQUE_INSTRUCTIONS
        from app.models.user import User
        
        technique = new_session.learning_mode if new_session.learning_mode in TECHNIQUE_INSTRUCTIONS else 'Deep Work'
        tech_info = TECHNIQUE_INSTRUCTIONS.get(technique)
        
        # Check focus threshold (Req: Startup Warning)
        user = User.query.get(user_id)
        user_focus_limit = user.focus_threshold if user else 60
        timer_config = tech_info['timer_config']
        
        # Startup Warning Overhaul
        if timer_config['duration'] > user_focus_limit:
            nudge = "Refocus Alert: Session exceeds your focus limit. Maintain high intensity to avoid distractions."
            
        # --- Rule Engine Real-Time Check ---
        from app.services.rule_engine import RuleEngine
        
        context = {
            'session_vibe': new_session.vibe,
            'current_session_duration': 0, # Start is 0
            'user_focus_threshold': user_focus_limit
        }
        
        active_rules = RuleEngine.evaluate_triggers(context)
        for rule in active_rules:
            # Flow Protection Check (First 50% check handled in real-time updates usually, but here for initial nudges)
            is_deep_work = (technique == 'Deep Work')
            if is_deep_work and "Breaks" in rule.tags:
                # "Suppress all 'Refocus Alerts'..." (originally Nudges/Breaks)
                print(f"Flow Protection: Suppressing alert '{rule.content}' for Deep Work session.")
                continue 
                
            if "Breaks" in rule.tags and new_session.vibe == 'High Frustration':
                 # Nudge Logic: Replace "Break" with "Refocus Alerts"
                 nudge = f"Refocus Alert: {rule.content} (Source: {rule.academic_source})"

        db.session.add(new_session)
        db.session.commit()
        
        return new_session, nudge, tech_info

    @staticmethod
    def log_distraction(session_id):
        session = StudySession.query.get(session_id)
        if not session: return False, "Session not found"
        
        if session.distraction_count >= 2:
            return False, "Distraction limit reached (Max 2)."
            
        session.distraction_count += 1
        db.session.commit()
        return True, f"Distraction logged. Count: {session.distraction_count}/2"

    @staticmethod
    def end_session(session_id, data):
        session = StudySession.query.get(session_id)
        if not session:
            return None, "Session not found"
            
        session.end_time = datetime.utcnow()
        # Ensure distraction_count is up to date if client sends it too, or trust server log?
        # User requirement: "Increment session.distraction_count per [log_distraction] call."
        # If client sends final count, it might overwrite? Let's assume server truth or client sync.
        # But for 'score'/success_score, client sends it.
        session.success_score = data.get('success_score', 0.0)
        
        # Calculate raw duration
        raw_duration = (session.end_time - session.start_time).total_seconds() / 60
        
        # Time Deductions: Variable Distraction Logic - Simplified
        total_distraction_seconds = data.get('total_distraction_seconds', 0)
        
        # Calculate deduction in minutes (float)
        distraction_minutes = total_distraction_seconds / 60.0
        
        # Safety Guard: Anomalous Data Check
        if total_distraction_seconds > (raw_duration * 60):
            print(f"WARNING: Anomalous distraction data: Distraction ({total_distraction_seconds}s) exceeds session duration ({raw_duration * 60}s).")
            # Log this properly in production, using print for now
            final_duration = 0
        else:
            # Final duration is raw duration minus distraction time, floored to 0
            # Must convert to int only after calculation to maintain precision
            final_duration = max(0, int(raw_duration - distraction_minutes))
        
        session.duration_minutes = final_duration
        
        # Disable 'Pause' functionality for Deep Work (Legacy logic check, keep pass)
        if session.learning_mode == 'Deep Work': # Removed pause_duration check
            pass
        
        # Award XP (Updated Signature)
        # Passing 'final_duration' (Net) and 'distraction_count' as requested
        xp = GamificationService.award_xp(
            session.user_id, 
            final_duration, 
            session.distraction_count
        )
        
        # Trigger Continuous Optimization (Inference)
        from app.services.inference_service import InferenceService
        InferenceService.optimize_schedule(session.user_id)
        
        # Save post-session feedback fields
        session.mood_after = data.get('mood_after')
        session.actual_duration_minutes = data.get('actual_duration_minutes')
        session.completed_on_time = data.get('completed_on_time', False)
        session.would_repeat = data.get('would_repeat')
        
        # Generate insight string from session data
        session.session_insight = generate_session_insight(session)
        
        db.session.commit()
        
        # Update streak after session completion
        GamificationService.calculate_streak(session.user_id)
        
        # ── Notification triggers via TriggerEvaluator (never crash session saving) ──
        try:
            from app.services.trigger_evaluator import TriggerEvaluator

            # Low efficacy session (score < 2)
            should_fire, ctx = TriggerEvaluator.check_low_efficacy_session(session.user_id, session.id)
            if should_fire:
                NotificationService.create_triggered_notification(session.user_id, 'low_efficacy_session', ctx)

            # Burnout warning (2+ low energy in last 3 sessions)
            should_fire, ctx = TriggerEvaluator.check_burnout_warning(session.user_id)
            if should_fire:
                NotificationService.create_triggered_notification(session.user_id, 'burnout_warning', ctx)

            # Badge earned (XP threshold crossed)
            should_fire, ctx = TriggerEvaluator.check_badge_earned(session.user_id)
            if should_fire:
                NotificationService.create_triggered_notification(session.user_id, 'badge_earned', ctx)

            # Streak milestone (7, 14, 30, 60 days)
            should_fire, ctx = TriggerEvaluator.check_streak_milestone(session.user_id)
            if should_fire:
                NotificationService.create_triggered_notification(session.user_id, 'streak_milestone', ctx)
        except Exception as e:
            print(f"[session_service] Notification trigger failed (non-fatal): {e}")
        
        return session, xp
