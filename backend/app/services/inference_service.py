from datetime import datetime, timedelta, time, timezone
from datetime import time as dt_time

from app import db
from app.models.session import ScheduleBlock
from app.models.course import Course
from app.models.timetable_entry import TimetableEntry
from app.services.rule_engine import RuleEngine


def get_blocked_slots(user_id: int) -> dict:
    '''
    Returns a dict of day → list of (start_time, end_time)
    tuples representing class times.
    '''
    entries = TimetableEntry.query.filter_by(
        user_id=user_id
    ).all()

    blocked = {}
    for entry in entries:
        day = entry.day_of_week
        if day not in blocked:
            blocked[day] = []
        blocked[day].append((entry.start_time, entry.end_time))

    return blocked


def is_slot_blocked(
    day: str,
    start: dt_time,
    end: dt_time,
    blocked_slots: dict
) -> bool:
    '''
    Returns True if the given time slot overlaps with any
    class on that day.
    '''
    if day not in blocked_slots:
        return False

    for (class_start, class_end) in blocked_slots[day]:
        if start < class_end and end > class_start:
            return True

    return False


def _hour_candidates(
    day_name: str,
    preferred_hour: int,
    blocked_slots: dict,
) -> list:
    '''Prefer slots after classes, then peak time, then evening.'''
    last_class_hour = 6
    for _start, end in blocked_slots.get(day_name, []):
        end_hour = end.hour + (1 if end.minute else 0)
        last_class_hour = max(last_class_hour, end_hour)

    candidates = []
    seen = set()

    def add(hour: int):
        if 7 <= hour <= 22 and hour not in seen:
            seen.add(hour)
            candidates.append(hour)

    for hour in range(max(7, last_class_hour), 23):
        add(hour)

    for offset in range(0, 16):
        for hour in (preferred_hour + offset, preferred_hour - offset):
            add(hour)

    for hour in (18, 19, 20, 21, 22):
        add(hour)

    return candidates


def _find_unblocked_hour(
    day_name: str,
    duration_minutes: int,
    preferred_hour: int,
    blocked_slots: dict,
    day_used_slots: list,
):
    '''Return a start hour with no class or study-block overlap, or None.'''
    candidates = _hour_candidates(day_name, preferred_hour, blocked_slots)

    for hour in candidates:
        candidate_start = time(hour, 0)
        end_dt = datetime.combine(
            datetime.today().date(), candidate_start
        ) + timedelta(minutes=duration_minutes)
        candidate_end = end_dt.time()

        if is_slot_blocked(
            day_name, candidate_start, candidate_end, blocked_slots
        ):
            continue

        overlaps_study = False
        for used_start, used_end in day_used_slots:
            if candidate_start < used_end and candidate_end > used_start:
                overlaps_study = True
                break
        if overlaps_study:
            continue

        return hour

    return None


# --- Template Configuration ---
TEMPLATE_CONFIG = {
    'pomodoro': {
        'technique_name': 'Pomodoro',
        'technique_details': 'Work for 25 minutes, take a 5-minute break. After 4 cycles, take a longer 15-minute break.',
        'base_duration': 25,
        'block_type': 'Pomodoro Session'
    },
    'deep_work': {
        'technique_name': 'Deep Work',
        'technique_details': 'Eliminate all distractions. Work with full concentration for the entire block.',
        'base_duration': None,
        'block_type': 'Deep Work'
    },
    'active_recall': {
        'technique_name': 'Active Recall (Blurting)',
        'technique_details': 'Write everything you know from memory, then check notes.',
        'base_duration': 45,
        'block_type': 'Active Recall'
    }
}


def get_alternate_technique(course_weight, template_key):
    """Return an alternate technique based on course weight."""
    if course_weight >= 4:
        return {
            'technique_name': 'Feynman Technique',
            'technique_details': 'Open a blank page. Write the topic at the top. Explain it simply as if teaching someone new to it. Where you get stuck is what to study next.',
            'block_type': 'Concept Mastery'
        }
    elif course_weight == 3:
        return {
            'technique_name': 'Blurting (Active Recall)',
            'technique_details': 'Close your notes. Write everything you remember about this topic. Then check what you missed.',
            'block_type': 'Active Recall'
        }
    else:
        return {
            'technique_name': 'Spaced Repetition Review',
            'technique_details': 'Review your notes from the last session on this topic. Focus on anything you found difficult before.',
            'block_type': 'Review Session'
        }


class InferenceService:
    @staticmethod
    def generate_week_schedule(user_id, selected_course_ids=None, week_start_override=None):
        from app.models.user import User
        LAGOS_TZ = timezone(timedelta(hours=1))

        user = User.query.get(user_id)
        if not user:
            return "User not found."

        # ── 1. FETCH USER CONTEXT ────────────────────────────────────
        user_context = RuleEngine.get_user_context(user_id)

        # Template detection — match against stored onboarding values
        raw_template = str(user.base_template or '').lower()

        if 'pomodoro' in raw_template or 'sprinter' in raw_template:
            template_key = 'pomodoro'
        elif 'deep' in raw_template or 'deepwork' in raw_template:
            template_key = 'deep_work'
        elif 'recall' in raw_template or 'recaller' in raw_template:
            template_key = 'active_recall'
        else:
            template_key = 'pomodoro'  # safe fallback, not deep work
            print(f"  WARNING: Unrecognised base_template '{raw_template}', defaulting to pomodoro", flush=True)

        template_cfg = TEMPLATE_CONFIG[template_key]

        peak_time_str = str(user.peak_time or "morning").lower()
        focus_threshold = user_context.get('focus_threshold')
        burnout_risk = user_context.get("burnout_risk", "Low")
        avg_efficacy = user_context.get("avg_session_efficacy", 1.0)

        # Peak-hour mapping
        peak_hour_map = {"morning": 8, "afternoon": 13, "evening": 18, "night": 18}
        base_peak = peak_hour_map.get(peak_time_str, 9)

        # Daily cognitive budget (cap 1–3)
        if user.daily_cognitive_budget:
            daily_budget = user.daily_cognitive_budget
        else:
            # daily_cognitive_budget is not set during onboarding, so derive from template.
            # Deep Work sessions are 90min — 2 blocks per day is the right load.
            # Pomodoro sessions are 25-50min — 3 blocks is manageable.
            # Active Recall is cognitively demanding — 2 blocks.
            template_budget_defaults = {
                'deep_work':     2,
                'active_recall': 2,
                'pomodoro':      3,
            }
            daily_budget = template_budget_defaults.get(template_key, 2)

        daily_budget = max(1, min(3, int(daily_budget)))

        # ── SUGGESTED STUDY CONDITIONS (Problem 4) ───────────────────
        env_map = {
            'silent': 'Library or Private Room',
            'ambient': 'Cafe or Lounge',
            'flexible': 'Any quiet space'
        }
        medium_map = {
            'visual': 'Diagrams, slides, or videos',
            'aural': 'Recorded lectures or verbal explanation',
            'read/write': 'Textbook, notes, or written summaries',
            'kinesthetic': 'Practice problems or hands-on exercises'
        }
        social_map = {
            'alone': 'Solo',
            'solo': 'Solo',
            'others': 'Group or Study Partner',
            'group': 'Group or Study Partner'
        }

        preferred_env = str(user.preferred_environment_v2 or user.environment_pref or '').lower()
        learning_style = str(user.learning_style or '').lower()
        social_mode = str(user.study_mode or user.study_social_pref or '').lower()

        suggested_environment = next((v for k, v in env_map.items() if k in preferred_env), 'Library or Private Room')
        suggested_medium = next((v for k, v in medium_map.items() if k in learning_style), 'Notes or written summaries')
        suggested_social_setting = next((v for k, v in social_map.items() if k in social_mode), 'Solo')

        # ── 2. COURSE RANKING (no shuffle) ───────────────────────────
        all_courses = (
            user.courses
            if not selected_course_ids
            else Course.query.filter(Course.id.in_(selected_course_ids)).all()
        )
        if not all_courses:
            return "No courses found."

        # Sorted descending by weight * credits — heaviest first
        ranked_courses = sorted(
            all_courses,
            key=lambda c: c.weight * c.credits,
            reverse=True,
        )

        def template_duration(slot_is_alternate: bool = False) -> int:
            if template_key == 'deep_work':
                base = user.zone_duration or 90
                if not slot_is_alternate and ranked_courses:
                    heaviest = ranked_courses[0]
                    if heaviest.weight >= 4:
                        base = min(base + 30, 120)
                return base
            return template_cfg['base_duration']

        # ── 3. CLEAR OLD BLOCKS ──────────────────────────────────────
        db.session.query(ScheduleBlock).filter_by(user_id=user.id).delete()

        # ── 4. ROTATIONAL QUEUE (respects ranking order) ─────────────
        course_queue = list(ranked_courses)

        # Track low efficacy flag for next-day technique swap
        apply_review_swap = False

        from app.services.timetable_service import user_has_timetable

        if user_has_timetable(user.id):
            blocked_slots = get_blocked_slots(user.id)
        else:
            blocked_slots = {}

        # ── 5. CALENDAR ALIGNMENT — start from Monday ────────────────
        today = datetime.now(LAGOS_TZ).date()
        if week_start_override:
            start_of_week = week_start_override
        else:
            start_of_week = today - timedelta(days=today.weekday())

        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            day_name = current_day.strftime("%A")
            is_sunday = day_name == "Sunday"

            # ─── STEP 1: Determine block count ───────────────────────
            day_block_count = daily_budget
            if is_sunday:
                day_block_count = min(day_block_count, 2)
            if burnout_risk == "High":
                day_block_count = max(1, day_block_count - 1)

            # ─── STEP 2: Select courses for today's slots ────────────
            used_today_ids = []
            day_courses = []

            for _ in range(day_block_count):
                if not course_queue:
                    course_queue = list(ranked_courses)
                selected = next(
                    (c for c in course_queue if c.id not in used_today_ids),
                    course_queue[0],
                )
                day_courses.append(selected)
                used_today_ids.append(selected.id)
                course_queue.remove(selected)

            # Heaviest course always goes in slot 1 (peak window)
            day_courses.sort(key=lambda c: c.weight * c.credits, reverse=True)

            # ─── Determine which slot gets alternate technique ───────
            # Problem 3: Per-day technique distribution
            # Peak slot (index 0) always uses primary template
            # Last slot uses alternate technique (if day > 1 block)
            if is_sunday:
                alternate_slot_idx = -1  # No alternate on Sunday
            elif day_block_count >= 2:
                alternate_slot_idx = day_block_count - 1  # Last slot
            else:
                alternate_slot_idx = -1  # Single block = always primary

            # ─── STEP 3–5: Build each block (with class conflict check) ─
            day_used_slots = []
            blocks_to_save = []

            for slot_idx, c_obj in enumerate(day_courses):
                preferred_hour = min(base_peak + (slot_idx * 3), 22)
                is_peak_slot = (slot_idx == 0)

                # --- Sunday: always Spaced Repetition ---
                if is_sunday:
                    tech_name = "Spaced Repetition"
                    tech_details = "Review previously studied material at increasing intervals. Focus on weak areas first."
                    block_type = "Review Session"
                    duration = 45

                # --- Alternate slot ---
                elif slot_idx == alternate_slot_idx:
                    alt = get_alternate_technique(c_obj.weight, template_key)
                    tech_name = alt['technique_name']
                    tech_details = alt['technique_details']
                    block_type = alt['block_type']
                    duration = template_duration(slot_is_alternate=True)
                    if tech_name == 'Blurting (Active Recall)':
                        duration = 35
                    elif tech_name == 'Spaced Repetition Review':
                        duration = 35

                # --- Primary template slot ---
                else:
                    tech_name = template_cfg['technique_name']
                    tech_details = template_cfg['technique_details']
                    block_type = template_cfg['block_type']
                    duration = template_duration()

                # Cap at focus_threshold
                if focus_threshold and isinstance(focus_threshold, int) and focus_threshold < duration:
                    duration = focus_threshold

                # Sunday cap
                if is_sunday:
                    duration = min(duration, 45)

                # Burnout reduction
                if burnout_risk == "High":
                    duration = max(25, duration - 15)

                # Low-efficacy review swap (from previous day's check)
                if apply_review_swap and not is_sunday and not is_peak_slot:
                    tech_name = "Spaced Repetition Review"
                    tech_details = (
                        "Re-cover weak material from recent sessions "
                        "before moving forward."
                    )

                # --- Rule engine refinement (schedule rules only) ---
                pred_ctx = RuleEngine.get_predictive_context(
                    user_id, day_name, preferred_hour
                )
                rule_context = user_context.copy()
                rule_context.update(
                    {
                        "course_weight": c_obj.weight,
                        "session_vibe": pred_ctx.get("session_vibe"),
                    }
                )
                matched_rules = RuleEngine.evaluate_triggers(
                    rule_context, context_type="schedule"
                )

                # Apply rule technique — only on non-peak slots, never Sunday
                # Peak slot (slot 0) is protected from rule overrides
                if matched_rules and not is_sunday and not is_peak_slot:
                    for rule in matched_rules:
                        p_lower = rule.principle.lower()
                        # Never let internal scheduling constraint rules surface as technique names
                        if 'template enforcement' in p_lower or 'template block sizing' in p_lower:
                            continue
                        tech_name = rule.principle
                        tech_details = rule.content

                # Rule-based duration adjustments
                for rule in matched_rules:
                    principle_lower = rule.principle.lower()
                    if "sprint" in principle_lower or "short" in principle_lower:
                        duration = max(25, duration - 15)
                    elif ("deep" in principle_lower or "extended" in principle_lower) and template_key == 'deep_work':
                        duration += 15
                        if focus_threshold and isinstance(focus_threshold, int) and duration > focus_threshold:
                            duration = focus_threshold

                # P5: Review techniques outside Sunday always 35 minutes
                if tech_name in ('Spaced Repetition Review', 'Blurting (Active Recall)') and day_name != 'Sunday':
                    duration = 35

                hour = _find_unblocked_hour(
                    day_name,
                    duration,
                    preferred_hour,
                    blocked_slots,
                    day_used_slots,
                )
                if hour is None:
                    blocks_to_save = None
                    break

                start_dt = datetime.combine(current_day, time(hour, 0))
                end_dt = start_dt + timedelta(minutes=duration)
                day_used_slots.append((start_dt.time(), end_dt.time()))

                blocks_to_save.append(
                    ScheduleBlock(
                        user_id=user.id,
                        date=current_day,
                        day_of_week=day_name,
                        start_time=start_dt.time(),
                        end_time=end_dt.time(),
                        block_type=block_type,
                        status="upcoming",
                        technique_name=tech_name,
                        technique_details=tech_details,
                        course_id=c_obj.id,
                        suggested_environment=suggested_environment,
                        suggested_social_setting=suggested_social_setting,
                        suggested_medium=suggested_medium,
                    )
                )

            if blocks_to_save is None:
                continue

            for block in blocks_to_save:
                db.session.add(block)

            # ─── End-of-day: check efficacy for next day swap ────────
            apply_review_swap = avg_efficacy is not None and avg_efficacy < 2.5

        db.session.commit()
        return "Adaptive Schedule Generated"

    @staticmethod
    def optimize_schedule(user_id):
        """Post-session optimization stub. Called by session_service after each session ends."""
        pass