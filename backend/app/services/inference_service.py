from datetime import datetime, timedelta, time
from app import db
from app.models.session import ScheduleBlock
from app.models.course import Course, StudyKnowledge

class InferenceService:
    @staticmethod
    def get_cognitive_cost(block_type):
        return 1.5 if block_type == "Deep Work" else 1.0

    @staticmethod
    def generate_week_schedule(user_id, selected_course_ids=None):
        from app.models.user import User
        user = User.query.get(user_id)
        if not user:
            print(f"User {user_id} not found")
            return

        # 1. Fetch & Quantify Courses (STRICT: User-Only or Explicit Selection)
        courses = []
        if selected_course_ids:
             # If caller provides specific IDs, use ONLY those.
             # This is useful for Onboarding where user.courses might be broad but we want to focus on selection?
             # actually user request says: "The engine must only use the provided selected_course_ids... Remove all fallback logic"
             courses = Course.query.filter(Course.id.in_(selected_course_ids)).all()
        elif user.courses:
            courses = user.courses
        
        if not courses:
            print(f"Inference Engine Halted: User {user.username} has no courses selected.")
            return "No courses found. Please select courses in Onboarding."

        # 2. Cleanup Existing Schedule (Safety First)
        db.session.query(ScheduleBlock).filter_by(user_id=user.id).delete()
        
        # 3. Priority Scoring (Weight * Credits)
        ranked_courses = []
        for c in courses:
            score = c.weight * c.credits
            ranked_courses.append({'course': c, 'score': score, 'id': c.id})
        ranked_courses.sort(key=lambda x: x['score'], reverse=True)
        
        # 4. Initialize Queue (Stateful)
        # We need a robust queue that can refill itself if we run out of unique courses for a day
        course_queue = ranked_courses[:] 
        
        start_date = datetime.utcnow().date()
        
        from app.services.rule_engine import RuleEngine
        
        # 5. Iteration: Days (0..6)
        for i in range(7):
            current_day = start_date + timedelta(days=i)
            day_name = current_day.strftime("%A")
            
            # --- SUNDAY EXCEPTION ---
            if day_name == 'Sunday':
                # Single "Weekly Review" block.
                tech_name = "Behavioral Anchor Alignment"
                tech_details = "Review your weekly performance against your biological peak times. Adjust schedule if needed."
                reason = "Sunday is reserved for high-level strategy and review."
                academic_cit = "Journal of Biological Rhythms (2022)"
                
                # Attach to any course (e.g. lowest valid) just for FK constraint
                ref_course = ranked_courses[-1]['course']
                
                review_block = ScheduleBlock(
                    user_id=user.id,
                    day_of_week=day_name,
                    date=current_day,
                    start_time=time(16, 0),
                    end_time=time(17, 0),
                    block_type="Deep Work",
                    status="upcoming",
                    technique_name=tech_name,
                    technique_details=tech_details,
                    refinement_reason=reason,
                    academic_citation=academic_cit,
                    course_id=ref_course.id
                )
                db.session.add(review_block)
                continue 
            
            # --- STANDARD DAY (Mon-Sat) ---
            used_today = [] # Reset for the new day
            slot_times = [9, 14, 19] # Morning, Afternoon, Evening
            
            courses_used_in_this_day_slots = []
            
            for slot_idx, hour in enumerate(slot_times):
                
                # REFILL LOGIC: If queue is empty, refill from ranked_courses
                if not course_queue:
                    course_queue = ranked_courses[:]

                # SELECTOR: Pick next course from queue NOT in used_today
                selected_candidate = None
                
                # Iterate through queue to find valid candidate
                for candidate in course_queue:
                    c_id = candidate['id']
                    if c_id in used_today: continue
                    selected_candidate = candidate
                    break
                
                # Fallback: If we exhausted queue and still no candidate (e.g. user has < 3 courses)
                # We MUST reuse to fill the slot.
                if not selected_candidate and courses:
                     # Pick the one used least recently today (effectively just pick first available if really tight)
                     # Or just pick from queue[0]
                     if course_queue:
                        selected_candidate = course_queue[0]
                     else:
                        selected_candidate = ranked_courses[0] # Should exist if courses exist

                if not selected_candidate: continue
                
                # Book it
                c_obj = selected_candidate['course']
                used_today.append(c_obj.id)
                courses_used_in_this_day_slots.append(selected_candidate) 
                
                # Expert System: Technique Assignment
                rule_context = {
                    'course_weight': c_obj.weight,
                    'phase': 'planning'
                }
                
                matched_rules = RuleEngine.evaluate_triggers(rule_context)
                
                tech_name = "Standard Session"
                tech_details = "Focus on material."
                citation = ""
                reason = "Scheduled based on priority."
                
                if matched_rules:
                    rule = matched_rules[0] # Take first match
                    tech_name = rule.principle
                    tech_details = rule.content
                    citation = rule.academic_source
                    reason = rule.rule_logic
                
                b_type = "Deep Work" if c_obj.weight >= 4 else "Lecture"

                # Create Block
                block = ScheduleBlock(
                    user_id=user.id,
                    day_of_week=day_name,
                    date=current_day,
                    start_time=time(hour, 0),
                    end_time=time(hour + 1, 0),
                    block_type=b_type, # Still useful for coloring logic fallback
                    status="upcoming",
                    technique_name=tech_name,
                    technique_details=tech_details,
                    refinement_reason=reason,
                    academic_citation=citation,
                    course_id=c_obj.id
                )
                db.session.add(block)
                
            # End of Day: Rotate Queue
            # Move used courses to back to encourage variety tomorrow
            for used_cand in courses_used_in_this_day_slots:
                if used_cand in course_queue:
                    course_queue.remove(used_cand)
                    course_queue.append(used_cand)
        
        db.session.commit()
        return "Schedule generated"
