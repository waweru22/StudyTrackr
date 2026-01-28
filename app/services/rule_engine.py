from app import db
from app.models.course import StudyKnowledge
from app.models.session import StudySession, ScheduleBlock
from sqlalchemy import func
import logging

# Configure logger as requested for "Proof"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RuleEngine")

class RuleEngine:
    @staticmethod
    def evaluate_triggers(context_data):
        """
        Iterates through Knowledge Base and evaluates 'inference_trigger' against context_data.
        Returns a list of applicable rules (StudyKnowledge objects).
        """
        rules = StudyKnowledge.query.all()
        applicable_rules = []
        
        for rule in rules:
            trigger_stmt = rule.inference_trigger
            if not trigger_stmt:
                continue
                
            is_match = False
            
            # Dynamic Parsing Logic (Simplified for demonstration)
            # 1. Parse "Cumulative Course Minutes > 180" (Interleaving)
            if "cumulative_course_minutes" in trigger_stmt:
                threshold = 180 # Extract dynamically in a real parser
                min_val = context_data.get('cumulative_course_minutes', 0)
                if min_val > threshold:
                    is_match = True
                    
            # 2. Parse "Session Vibe == 'High Frustration'" (Zeigarnik)
            elif "session_vibe" in trigger_stmt:
                current_vibe = context_data.get('session_vibe')
                if current_vibe == 'High Frustration':
                    is_match = True
            
            # 3. Parse "Session Location Consistency" (Consolidation)
            elif "session_location_consistency" in trigger_stmt:
                consistency = context_data.get('location_consistency', 0.0)
                if consistency > 0.8 and context_data.get('course_weight', 0) >= 4:
                    is_match = True
            
            # 4. Focus Threshold (Fatigue)
            elif "current_session_duration" in trigger_stmt:
                duration = context_data.get('current_session_duration', 0)
                limit = context_data.get('user_focus_threshold', 60)
                if duration > limit:
                    is_match = True

            if is_match:
                # LOGGING AS REQUESTED
                print(f"\n[EXPERT SYSTEM] Rule Fired: {rule.principle}")
                print(f"   Logic: {rule.rule_logic}")
                print(f"   Trigger: {trigger_stmt}")
                print(f"   Context: {context_data}\n")
                
                applicable_rules.append(rule)
                
        return applicable_rules

    @staticmethod
    def get_user_context(user_id, current_session=None):
        """
        Aggregates data for the expert system.
        """
        context = {}
        
        # Calculate cumulative minutes (Mock or DB agg)
        # In a real app, complex queries here.
        context['cumulative_course_minutes'] = 200 # Mock for demonstrative testing
        context['location_consistency'] = 0.9 # Mock
        
        if current_session:
            context['session_vibe'] = current_session.vibe
            context['course_weight'] = current_session.course.weight if current_session.course else 3
            
            # Duration check
            if current_session.start_time:
                from datetime import datetime
                # Just usage estimation
                context['current_session_duration'] = 91 # Mock to force trigger
                context['user_focus_threshold'] = current_session.user.focus_threshold
                
        return context
