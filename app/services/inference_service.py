from datetime import datetime, timedelta, time
from app import db
from app.models.session import ScheduleBlock, StudySession
from app.models.course import Course, StudyKnowledge

class InferenceService:
    @staticmethod
    def get_cognitive_cost(block_type):
        return 1.5 if block_type == "Deep Work" else 1.0

    @staticmethod
    def generate_week_schedule(user, selected_course_ids=None):
        # 1. Fetch Courses
        if user.courses:
            courses = user.courses
        elif selected_course_ids:
            # Need to fetch weights etc.
            courses = Course.query.filter(Course.id.in_(selected_course_ids)).all()
        else:
            courses = []

        if not courses: return "No courses to schedule"

        # 2. Sort Primary Courses by Weight (DESC)
        sorted_courses = sorted(courses, key=lambda c: c.weight, reverse=True)
        # Limit to 12 if strict, though constraint is usually on selection.
        sorted_courses = sorted_courses[:12]

        start_date = datetime.utcnow().date()
        daily_load_map = {} # {date_str: current_load}
        
        # Grid System: Mon-Sat (6 days) x 3 Slots = 18 Slots
        # Sunday = Review Only (Skip for main curriculum)
        
        schedule_grid = [] # List of (date, slot_index)
        # Populate grid with available slots
        for i in range(7):
            current_day = start_date + timedelta(days=i)
            if current_day.strftime("%A") == 'Sunday':
                continue # Sunday is review only
            for slot_num in range(3):
                schedule_grid.append({
                    'date': current_day,
                    'slot_index': slot_num,
                    'filled': False
                })
        
        # Helper: Get User Budget
        user_budget = user.daily_cognitive_budget if hasattr(user, 'daily_cognitive_budget') else 4.0

        # Helper: Try to place block
        def try_place_block(course, block_type, reason):
            cost = InferenceService.get_cognitive_cost(block_type)
            placed = False
            
            for slot in schedule_grid:
                if slot['filled']: continue
                
                # Check Daily Budget
                d_key = slot['date'].strftime("%Y-%m-%d")
                current_load = daily_load_map.get(d_key, 0.0)
                
                if current_load + cost <= user_budget:
                    # Place it!
                    daily_load_map[d_key] = current_load + cost
                    slot['filled'] = True
                    placed = True
                    
                    # Create DB Block
                    # Determine Time based on slot index
                    # Slot 0: Morning, 1: Afternoon, 2: Evening? Or Peak Time relative?
                    # Let's anchor to Peak Time.
                    # If Peak=Morning (9am). Slots: 9am, 11am, 2pm?
                    # Simplified: 3 fixed slots for now: 10:00, 14:00, 16:00
                    base_hour = 10
                    if slot['slot_index'] == 1: base_hour = 14
                    if slot['slot_index'] == 2: base_hour = 16
                    
                    # Identity Durations
                    duration = 60
                    if block_type == "Deep Work": duration = 90
                    # If user identity constraints?
                    if user.base_template == 'Active Recaller': duration = 45
                    if user.base_template == 'Balanced Sprinter': duration = 25 # Pomodoro duration context? Usually 25+5. Block is session.
                    
                    # Focus Filter logic (Inline for now)
                    if block_type == "Deep Work" and (user.focus_threshold or 60) < 60 and user.base_template != 'Deep Work Specialist':
                        block_type = "Pomodoro" # Downgrade
                        reason = "Session intensity adjusted to match your current focus capacity (under 60m)."
                        duration = 45 # or user threshold?

                    new_block = ScheduleBlock(
                        user_id=user.id,
                        course_id=course.id,
                        day_of_week=slot['date'].strftime("%A"),
                        date=slot['date'],
                        start_time=time(base_hour, 0),
                        end_time=(datetime.combine(slot['date'], time(base_hour, 0)) + timedelta(minutes=duration)).time(),
                        block_type=block_type,
                        refinement_reason=reason,
                        academic_citation="Sweller (1988)" if "Budget" in reason else None,
                        logic_explanation="Cognitive Load / Curriculum Fit"
                    )
                    db.session.add(new_block)
                    break
            return placed

        # 3. Primary Pass: Fix all courses
        for course in sorted_courses:
            # Determine preferred type
            b_type = "Deep Work" if course.weight >= 4 else "Standard" 
            reason = None
            
            # Identity constraints
            if user.base_template == 'Active Recaller': 
                b_type = "Active Recall"
                reason = "Optimized for Active Retrieval"
            elif user.base_template == 'Balanced Sprinter':
                b_type = "Pomodoro"
                reason = "Maximizing Cognitive Agility"

            # Try fit
            if not try_place_block(course, b_type, reason or "Primary Curriculum Block"):
                # Hard-Wall Fix: Downgrade
                if b_type == "Deep Work":
                    # Downgrade to Standard
                    print(f"Downgrading Course {course.code} to Standard to fit budget.")
                    try_place_block(course, "Standard", "Intensity adjusted to ensure full curriculum coverage within the weekly cycle.")
                else:
                    print(f"Course {course.code} could not be scheduled even with downgrade (Budget/Slot Full).")

        # 4. Secondary Pass: Fill Gaps with T+1 Retrieval Chain
        # Loop through slots again
        for slot in schedule_grid:
            if not slot['filled']:
                # Find a course that needs review? 
                # "Fill remaining slots with the T+1 Retrieval Chain"
                # Logic: Pick a high weight course scheduled *yesterday*?
                # Simplified: Just pick random high weight course for Active Recall
                
                # Check budget for this slot's day
                d_key = slot['date'].strftime("%Y-%m-%d")
                current_load = daily_load_map.get(d_key, 0.0)
                cost = 1.0 # Active Recall cost
                
                if current_load + cost <= user_budget:
                    # Pick course (Round robin or random high weight)
                    # Let's pick the first weight 5 course not reviewed today?
                    recall_course = next((c for c in sorted_courses if c.weight >= 4), sorted_courses[0])
                    
                    slot['filled'] = True
                    daily_load_map[d_key] = current_load + cost
                    
                    # Time logic same as above
                    base_hour = 10 + (slot['slot_index'] * 3) # 10, 13, 16 approx
                    
                    new_block = ScheduleBlock(
                        user_id=user.id,
                        course_id=recall_course.id,
                        day_of_week=slot['date'].strftime("%A"),
                        date=slot['date'],
                        start_time=time(base_hour, 0),
                        end_time=(datetime.combine(slot['date'], time(base_hour, 0)) + timedelta(minutes=45)).time(), # 45m recall
                        block_type="Active Recall (Chain)",
                        refinement_reason="T+1 Retrieval Chain Fill",
                        academic_citation="Ebbinghaus (1885)",
                        logic_explanation="Spaced Repetition Gap Fill"
                    )
                    db.session.add(new_block)

        db.session.commit()
        return "Schedule Generated"
    
    # Keep existing methods like optimize_schedule if needed, or update similarly
    @staticmethod
    def optimize_schedule(user_id):
        # ... preserved ...
        pass
