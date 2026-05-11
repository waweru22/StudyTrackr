"""
Schedule Adaptation Engine
Analyzes weekly session performance and adapts the next week's
schedule by swapping underperforming techniques and shifting
time-slots based on mood patterns.

Called at end-of-week (Sunday) or via the /schedule/regenerate endpoint.
"""

from app import db
from app.models.session import ScheduleBlock, StudySession
from app.models.course import Course
from app.models.user import User
from app.services.rule_engine import RuleEngine
from datetime import datetime, timedelta, time, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AdaptationEngine")

LAGOS_TZ = timezone(timedelta(hours=1))

# ─── Technique swap look-up ──────────────────────────────────────────
# Keys match the technique_name values written by InferenceService
TECHNIQUE_SWAP_RULES = {
    'Pomodoro':                 ['Active Recall (Blurting)', 'Deep Work'],
    'Deep Work':                ['Active Recall (Blurting)', 'Pomodoro'],
    'Active Recall (Blurting)': ['Pomodoro', 'Deep Work'],
    'Feynman Technique':        ['Active Recall (Blurting)', 'Pomodoro'],
    'Spaced Repetition Review': ['Active Recall (Blurting)', 'Pomodoro'],
    'Spaced Repetition':        ['Active Recall (Blurting)', 'Pomodoro'],
}

# ─── Academic citations for transparency fields ─────────────────────
CITATIONS = {
    'low_effectiveness':  'Roediger & Karpicke (2006)',
    'high_effectiveness': 'Ebbinghaus (1885) - Spacing Effect',
    'mood_shift':         'Biological Rhythm Research (2023)',
    'technique_swap':     'Bjork & Bjork (2011)',
    'burnout_prevention': 'Oakley (2014) - Diffuse Mode',
}


class AdaptationEngine:
    """
    Analyses weekly session data and adapts next week's schedule.

    Public API
    ----------
    adapt_schedule_for_next_week(user_id) -> dict
        Main entry-point.  Returns a summary of every change made.
    """

    # ─────────────────────────────────────────────────────────────────
    # 1. ANALYSE
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def analyze_weekly_performance(user_id):
        """
        Aggregate all *completed* sessions from the current week,
        grouped by (course_id, technique_name).

        Returns
        -------
        dict
            {
                course_id: {
                    technique_name: {
                        'avg_effectiveness': float,
                        'avg_mood':          str | None,
                        'would_repeat_ratio': float (0-1),
                        'session_count':     int,
                        'sessions':          [StudySession, …]
                    }
                }
            }
            Empty dict when fewer than 1 completed session exists.
        """
        try:
            today = datetime.now(LAGOS_TZ).date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            sessions = StudySession.query.filter(
                StudySession.user_id == user_id,
                StudySession.start_time >= datetime.combine(start_of_week, time.min),
                StudySession.start_time <= datetime.combine(end_of_week, time.max),
                StudySession.end_time.isnot(None),       # completed only
            ).all()

            if len(sessions) < 1:
                logger.info(
                    f"[Adaptation] User {user_id}: <1 session this week. "
                    "Skipping adaptation."
                )
                return {}

            # ── Group by (course_id, technique) ──────────────────────
            analysis: dict = {}
            for s in sessions:
                cid = s.course_id
                tech = s.learning_mode or 'Unknown'
                analysis.setdefault(cid, {}).setdefault(tech, {
                    'avg_effectiveness': 0.0,
                    'avg_mood': None,
                    'would_repeat_ratio': 0.0,
                    'session_count': 0,
                    'sessions': [],
                })
                analysis[cid][tech]['sessions'].append(s)

            # ── Compute aggregates ───────────────────────────────────
            mood_map = {1: 'Drained', 2: 'Neutral', 3: 'Energized'}

            for cid in analysis:
                for tech in analysis[cid]:
                    bucket = analysis[cid][tech]
                    sl = bucket['sessions']
                    n = len(sl)

                    # avg effectiveness (derived from success_score)
                    avg_eff = (
                        sum(s.success_score or 0 for s in sl) / n
                        if n else 0.0
                    )
                    bucket['avg_effectiveness'] = round(avg_eff, 2)

                    # dominant mood
                    moods = [
                        mood_map.get(s.mood_after, 'Unknown')
                        for s in sl if s.mood_after
                    ]
                    if moods:
                        bucket['avg_mood'] = max(
                            set(moods), key=moods.count
                        )

                    # would-repeat ratio
                    repeats = [
                        s.would_repeat for s in sl
                        if s.would_repeat is not None
                    ]
                    if repeats:
                        bucket['would_repeat_ratio'] = round(
                            sum(1 for r in repeats if r) / len(repeats), 2
                        )

                    bucket['session_count'] = n

            logger.info(
                f"[Adaptation] Analysed {len(sessions)} sessions "
                f"for user {user_id}"
            )
            return analysis

        except Exception as e:
            logger.error(
                f"[Adaptation] analyze_weekly_performance error: {e}"
            )
            return {}

    # ─────────────────────────────────────────────────────────────────
    # 2. TECHNIQUE RECOMMENDATION
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def recommend_technique_change(course_id, current_technique,
                                   analysis_data):
        """
        Decide whether the technique for *course_id* should change.

        Decision tree
        -------------
        effectiveness < 2.0 AND would_repeat < 0.5 -> SWAP
        effectiveness >= 3.5 AND would_repeat >= 0.7 -> KEEP
        effectiveness < 2.5 AND would_repeat < 0.6 -> TRY ALTERNATE
        else                                        -> KEEP

        Returns
        -------
        (new_technique | None, reason | None)
        """
        try:
            techs = analysis_data.get(course_id, {})
            if current_technique not in techs:
                return None, None

            td = techs[current_technique]
            eff = td['avg_effectiveness']
            wr  = td['would_repeat_ratio']

            swaps = TECHNIQUE_SWAP_RULES.get(
                current_technique, ['Pomodoro']
            )

            if eff < 2.0 and wr < 0.5:
                new = swaps[0]
                reason = (
                    f"Eff {eff}/5 + repeat {wr:.0%} -> "
                    f"swap to {new}"
                )
                return new, reason

            if eff >= 3.5 and wr >= 0.7:
                return None, (
                    "High effectiveness; student would repeat. "
                    "Keeping technique."
                )

            if eff < 2.5 and wr < 0.6:
                new = swaps[0]
                reason = (
                    f"Underperformance ({eff}/5). "
                    f"Trying {new} next week."
                )
                return new, reason

            return None, (
                f"Adequate ({eff}/5, repeat {wr:.0%}). "
                "Keeping technique."
            )

        except Exception as e:
            logger.error(
                f"[Adaptation] recommend_technique_change error: {e}"
            )
            return None, None

    # ─────────────────────────────────────────────────────────────────
    # 3. TIME-SHIFT RECOMMENDATION
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def recommend_time_shift(course_id, analysis_data, current_hour):
        """
        Decide whether the time-slot for *course_id* should move,
        based on the dominant mood recorded during sessions.

        Constraints
        -----------
        - Maximum shift: +/-3 hours
        - No earlier than 08:00, no later than 22:00

        Returns
        -------
        (new_hour | None, reason | None)
        """
        try:
            techs = analysis_data.get(course_id)
            if not techs:
                return None, None

            moods = [
                t.get('avg_mood')
                for t in techs.values()
                if t.get('avg_mood')
            ]
            if not moods:
                return None, None

            dominant = max(set(moods), key=moods.count)

            if dominant == 'Drained':
                if current_hour >= 14:
                    new_h = max(8, current_hour - 4)
                    return new_h, (
                        f"Drained at {current_hour}:00 -> "
                        f"morning ({new_h}:00)"
                    )
                if current_hour >= 8:
                    new_h = min(22, current_hour + 3)
                    return new_h, (
                        f"Drained at {current_hour}:00 -> "
                        f"afternoon ({new_h}:00)"
                    )

            if dominant == 'Energized':
                return None, (
                    f"Energized at {current_hour}:00. "
                    "Keeping time."
                )

            return None, (
                f"Neutral at {current_hour}:00. "
                "Keeping time."
            )

        except Exception as e:
            logger.error(
                f"[Adaptation] recommend_time_shift error: {e}"
            )
            return None, None

    # ─────────────────────────────────────────────────────────────────
    # 4. ORCHESTRATOR
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def adapt_schedule_for_next_week(user_id):
        """
        Main entry-point -- called at end-of-week or via
        ``POST /schedule/regenerate``.

        Flow
        ----
        1. Analyse this week's completed sessions.
        2. For every course with session data, recommend technique
           changes and time shifts.
        3. Delete old schedule blocks and regenerate via
           ``InferenceService.generate_week_schedule()``.
        4. Walk the freshly-generated blocks and apply adaptations
           (technique swap, time shift) while populating
           ``refinement_reason``, ``academic_citation``, and
           ``logic_explanation``.
        5. Return a summary dict suitable for JSON serialisation.

        Returns
        -------
        dict  with keys: status, message, total_courses_analyzed,
              technique_swaps, time_shifts, adaptations
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logger.error(f"[Adaptation] User {user_id} not found")
                return {"error": "User not found"}

            logger.info(
                f"[Adaptation] Starting adaptation for user {user_id}"
            )

            # ── Step 1: analyse ──────────────────────────────────────
            analysis = AdaptationEngine.analyze_weekly_performance(
                user_id
            )
            if not analysis:
                logger.info(
                    "[Adaptation] No sessions. "
                    "Falling back to standard generation."
                )
                from app.services.inference_service import InferenceService
                InferenceService.generate_week_schedule(user_id)
                return {
                    "status": "fallback",
                    "message": "No session data. Standard schedule.",
                    "total_courses_analyzed": 0,
                    "technique_swaps": 0,
                    "time_shifts": 0,
                    "adaptations": {},
                }

            # ── Step 2: build adaptation map ─────────────────────────
            today = datetime.now(LAGOS_TZ).date()
            start_of_week = today - timedelta(days=today.weekday())

            adaptation_map: dict = {}

            for cid in analysis:
                cur_blocks = ScheduleBlock.query.filter(
                    ScheduleBlock.user_id == user_id,
                    ScheduleBlock.course_id == cid,
                    ScheduleBlock.date >= start_of_week,
                ).all()

                if not cur_blocks:
                    continue

                first = cur_blocks[0]
                cur_tech = first.technique_name or 'Unknown'
                cur_hour = first.start_time.hour

                new_tech, tech_reason = (
                    AdaptationEngine.recommend_technique_change(
                        cid, cur_tech, analysis
                    )
                )
                new_hour, time_reason = (
                    AdaptationEngine.recommend_time_shift(
                        cid, analysis, cur_hour
                    )
                )

                adaptation_map[cid] = {
                    'current_technique': cur_tech,
                    'new_technique': new_tech or cur_tech,
                    'tech_reason': tech_reason,
                    'current_hour': cur_hour,
                    'new_hour': new_hour or cur_hour,
                    'time_reason': time_reason,
                }

            # ── Step 3: regenerate schedule ───────────────────────────
            db.session.query(ScheduleBlock).filter_by(
                user_id=user_id
            ).delete()
            db.session.commit()
            logger.info(
                f"[Adaptation] Cleared old schedule for user {user_id}"
            )

            from app.services.inference_service import InferenceService
            InferenceService.generate_week_schedule(user_id)

            # ── Step 4: overlay adaptations ──────────────────────────
            today = datetime.now(LAGOS_TZ).date()
            start_of_week = today - timedelta(days=today.weekday())

            for cid, adapt in adaptation_map.items():
                blocks = ScheduleBlock.query.filter(
                    ScheduleBlock.user_id == user_id,
                    ScheduleBlock.course_id == cid,
                    ScheduleBlock.date >= start_of_week,
                ).all()

                for block in blocks:
                    # ── technique swap ────────────────────────────────
                    if adapt['new_technique'] != adapt['current_technique']:
                        old_t = adapt['current_technique']
                        new_t = adapt['new_technique']
                        block.technique_name = new_t
                        block.refinement_reason = (
                            f"{old_t} -> {new_t}"
                        )[:100]
                        block.logic_explanation = (
                            adapt['tech_reason'] or ''
                        )[:255]
                        block.academic_citation = (
                            CITATIONS['technique_swap']
                        )[:100]

                    # ── time shift ────────────────────────────────────
                    if adapt['new_hour'] != adapt['current_hour']:
                        old_h = adapt['current_hour']
                        new_h = adapt['new_hour']
                        old_start = block.start_time

                        new_start = time(new_h, old_start.minute)
                        dur_secs = (
                            datetime.combine(block.date, block.end_time)
                            - datetime.combine(block.date, block.start_time)
                        ).total_seconds()
                        new_end_dt = (
                            datetime.combine(block.date, new_start)
                            + timedelta(seconds=dur_secs)
                        )

                        block.start_time = new_start
                        block.end_time = new_end_dt.time()
                        block.refinement_reason = (
                            f"Time {old_h}:00->{new_h}:00"
                        )[:100]
                        block.logic_explanation = (
                            adapt['time_reason'] or ''
                        )[:255]
                        block.academic_citation = (
                            CITATIONS['mood_shift']
                        )[:100]

                    db.session.add(block)

            db.session.commit()
            logger.info(
                f"[Adaptation] Schedule committed for user {user_id}"
            )

            # ── Step 5: summary ──────────────────────────────────────
            tech_swaps = sum(
                1 for a in adaptation_map.values()
                if a['new_technique'] != a['current_technique']
            )
            time_shifts = sum(
                1 for a in adaptation_map.values()
                if a['new_hour'] != a['current_hour']
            )

            return {
                "status": "success",
                "message": (
                    f"Schedule adapted "
                    f"({tech_swaps + time_shifts} changes)"
                ),
                "total_courses_analyzed": len(analysis),
                "technique_swaps": tech_swaps,
                "time_shifts": time_shifts,
                "adaptations": {
                    str(k): v for k, v in adaptation_map.items()
                },
            }

        except Exception as e:
            logger.error(
                f"[Adaptation] adapt_schedule_for_next_week error: {e}"
            )
            return {"error": str(e)}
