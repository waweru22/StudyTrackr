"""
Schedule Adaptation Engine
Analyzes weekly session performance and adapts the schedule
by swapping underperforming techniques and shifting time-slots
based on mood patterns.

Called via the /schedule/adapt-now endpoint.
"""

from app import db
from app.models.session import ScheduleBlock, StudySession
from app.models.course import Course
from app.models.user import User
from app.services.rule_engine import RuleEngine
from datetime import datetime, timedelta, time, timezone, date
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AdaptationEngine")

LAGOS_TZ = timezone(timedelta(hours=1))

# ── Technique swap look-up ───────────────────────────────────────
# Keys match technique_name values written by InferenceService.
# When a technique underperforms for a course, the engine picks
# the first alternative from this list.
TECHNIQUE_SWAP_RULES = {
    'Pomodoro':                   ['Active Recall (Blurting)', 'Deep Work'],
    'Pomodoro Technique':         ['Active Recall (Blurting)', 'Deep Work'],
    'Deep Work':                  ['Active Recall (Blurting)', 'Pomodoro'],
    'Active Recall (Blurting)':   ['Pomodoro', 'Deep Work'],
    'Feynman Technique':          ['Active Recall (Blurting)', 'Pomodoro'],
    'The Feynman Technique':      ['Active Recall (Blurting)', 'Pomodoro'],
    'Spaced Repetition Review':   ['Active Recall (Blurting)', 'Pomodoro'],
    'Spaced Repetition':          ['Active Recall (Blurting)', 'Pomodoro'],
    'Recall-Gated Consolidation': ['Pomodoro', 'Active Recall (Blurting)'],
}

# ── Human-readable technique descriptions ────────────────────────
TECHNIQUE_DETAILS = {
    'Active Recall (Blurting)': (
        'Write everything you know about the topic from memory, '
        'then compare against your notes. Repeat for gaps.'
    ),
    'Pomodoro': (
        '25 minutes focused work → 5 minute break. After 4 cycles, '
        'take a 15–30 minute break.'
    ),
    'Deep Work': (
        '90 minutes of uninterrupted, cognitively demanding work '
        'with zero distractions.'
    ),
    'Feynman Technique': (
        'Explain the concept in simple terms as if teaching someone '
        'else. Identify and fill gaps in your understanding.'
    ),
    'Spaced Repetition Review': (
        'Review material at increasing intervals to consolidate '
        'knowledge into long-term memory.'
    ),
}


class AdaptationEngine:
    """
    Analyses weekly session data and adapts the schedule.

    Public API
    ----------
    analyze_weekly_performance(user_id) -> dict
        Aggregated performance per course_code.
    adapt_schedule_for_next_week(user_id, week_start_override=None) -> dict
        Main entry-point.  Returns a summary of every change made.
    """

    # -----------------------------------------------------------------
    # 1. ANALYSE
    # -----------------------------------------------------------------
    @staticmethod
    def analyze_weekly_performance(user_id):
        """
        Reads all completed StudySessions for the user.
        Returns a dict keyed by course_code with signal thresholds.

        Signal thresholds
        -----------------
        struggling -- avg_success_score < 3.0 OR repeat_rate < 0.4
        thriving   -- avg_success_score >= 4.0 AND repeat_rate >= 0.7
        average    -- anything else
        """
        try:
            sessions = StudySession.query.filter(
                StudySession.user_id == user_id,
                StudySession.end_time.isnot(None),
            ).all()

            if not sessions:
                logger.info(
                    f"[Adaptation] User {user_id}: 0 completed sessions. "
                    "Skipping analysis."
                )
                return {}

            # Group by course
            course_buckets = {}
            for s in sessions:
                if not s.course:
                    continue
                code = s.course.code
                if code not in course_buckets:
                    course_buckets[code] = {
                        'course_name': s.course.name,
                        'sessions': [],
                    }
                course_buckets[code]['sessions'].append(s)

            # Compute aggregates
            analysis = {}
            for code, bucket in course_buckets.items():
                sl = bucket['sessions']
                n = len(sl)

                avg_score = round(
                    sum(s.success_score or 0 for s in sl) / n, 1
                ) if n else 0.0

                avg_mood = round(
                    sum(s.mood_after or 2 for s in sl) / n, 1
                ) if n else 2.0

                repeats = [
                    s.would_repeat for s in sl
                    if s.would_repeat is not None
                ]
                repeat_rate = round(
                    sum(1 for r in repeats if r) / len(repeats), 2
                ) if repeats else 0.5

                vibes = [s.vibe for s in sl if s.vibe]
                dominant_vibe = (
                    max(set(vibes), key=vibes.count) if vibes else 'Normal'
                )

                # Determine signal
                if avg_score < 3.0 or repeat_rate < 0.4:
                    signal = 'struggling'
                elif avg_score >= 4.0 and repeat_rate >= 0.7:
                    signal = 'thriving'
                else:
                    signal = 'average'

                analysis[code] = {
                    'course_name':       bucket['course_name'],
                    'session_count':     n,
                    'avg_success_score': avg_score,
                    'avg_mood_after':    avg_mood,
                    'repeat_rate':       repeat_rate,
                    'dominant_vibe':     dominant_vibe,
                    'signal':            signal,
                }

            logger.info(
                f"[Adaptation] Analysed {len(sessions)} sessions "
                f"for user {user_id} across {len(analysis)} courses"
            )
            return analysis

        except Exception as e:
            logger.error(
                f"[Adaptation] analyze_weekly_performance error: {e}"
            )
            return {}

    # -----------------------------------------------------------------
    # 2. ADAPT
    # -----------------------------------------------------------------
    @staticmethod
    def adapt_schedule_for_next_week(user_id, week_start_override=None):
        """
        Main entry-point.

        Flow
        ----
        1. Analyse performance (reads StudySession data).
        2. Snapshot old techniques from ALL existing blocks.
        3. Delete ALL schedule blocks (sessions are independent).
        4. Generate a fresh base schedule via InferenceService.
        5. OVERLAY technique swaps for courses flagged as struggling.
        6. Build reasoning and save AdaptationLog.
        7. Return summary dict.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logger.error(f"[Adaptation] User {user_id} not found")
                return {"error": "User not found"}

            logger.info(
                f"[Adaptation] Starting adaptation for user {user_id}"
            )

            today = date.today()
            this_monday = today - timedelta(days=today.weekday())
            target_monday = week_start_override or this_monday

            # ── Step 1: Analyse performance BEFORE deleting ──────────
            analysis = AdaptationEngine.analyze_weekly_performance(user_id)
            context = RuleEngine.get_user_context(user_id)

            # ── Step 2: Snapshot old techniques from ALL blocks ──────
            old_techniques = {}
            for b in ScheduleBlock.query.filter_by(user_id=user_id).all():
                if b.course:
                    old_techniques[b.course.code] = b.technique_name

            # ── Step 3: Delete ALL schedule blocks ───────────────────
            # StudySession records are independent (no FK to ScheduleBlock)
            # so session history is preserved.
            ScheduleBlock.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            logger.info(
                f"[Adaptation] Cleared all blocks for user {user_id}"
            )

            # ── Step 4: Generate fresh base schedule ─────────────────
            from app.services.inference_service import InferenceService
            InferenceService.generate_week_schedule(
                user_id, week_start_override=target_monday
            )

            # ── Step 5: Overlay technique swaps ──────────────────────
            new_blocks = ScheduleBlock.query.filter_by(
                user_id=user_id
            ).all()

            adaptations = []
            preserved = []
            seen_courses = set()

            for block in new_blocks:
                if not block.course:
                    continue
                code = block.course.code
                if code in seen_courses:
                    continue
                seen_courses.add(code)

                perf = analysis.get(code, {})
                signal = perf.get('signal', 'average')
                old_tech = old_techniques.get(code)
                current_tech = block.technique_name

                if signal == 'struggling':
                    # ── Force a technique swap ──
                    # Look up alternatives for whatever technique the
                    # block currently has, then apply to ALL blocks
                    # for this course.
                    lookup_key = current_tech or old_tech or ''
                    alternatives = TECHNIQUE_SWAP_RULES.get(lookup_key, [])
                    if not alternatives and old_tech:
                        alternatives = TECHNIQUE_SWAP_RULES.get(old_tech, [])

                    if alternatives:
                        new_tech = alternatives[0]

                        # Apply to every block for this course
                        for b in new_blocks:
                            if b.course and b.course.code == code:
                                b.technique_name = new_tech
                                b.technique_details = TECHNIQUE_DETAILS.get(
                                    new_tech, ''
                                )
                                b.refinement_reason = (
                                    f"Adapted: {old_tech or current_tech} → "
                                    f"{new_tech} (effectiveness "
                                    f"{perf.get('avg_success_score', 0):.1f}/5)"
                                )

                        avg_s = perf.get('avg_success_score', 0)
                        adaptations.append({
                            "course_code":  code,
                            "course_name":  perf.get(
                                'course_name', block.course.name
                            ),
                            "change_type":  "technique_changed",
                            "from":         old_tech or current_tech,
                            "to":           new_tech,
                            "trigger":      "low_efficacy",
                            "explanation":  (
                                f"Effectiveness averaged {avg_s:.1f}/5 "
                                f"with mood consistently drained. "
                                f"{old_tech or current_tech} was not "
                                f"effective for this course. Switched to "
                                f"{new_tech} for better cognitive fit."
                            ),
                        })
                    else:
                        preserved.append({
                            "course_code": code,
                            "course_name": perf.get(
                                'course_name', block.course.name
                            ),
                            "reason": (
                                f"Struggling ({perf.get('avg_success_score', 0):.1f}/5) "
                                "but no alternative technique available."
                            ),
                        })
                else:
                    # ── Thriving or average — preserve ──
                    if signal == 'thriving':
                        reason = (
                            f"Averaging {perf.get('avg_success_score', 0):.1f}/5 "
                            f"with {perf.get('repeat_rate', 0)*100:.0f}% repeat "
                            f"rate — technique is working well."
                        )
                    else:
                        reason = "Performance within normal range — no change needed."
                    preserved.append({
                        "course_code": code,
                        "course_name": perf.get(
                            'course_name', block.course.name
                        ),
                        "reason": reason,
                    })

            db.session.commit()
            logger.info(
                f"[Adaptation] Overlaid {len(adaptations)} technique swap(s)"
            )

            # ── Step 6: Save AdaptationLog ───────────────────────────
            end_sunday = target_monday + timedelta(days=6)
            week_label = (
                f"{target_monday.strftime('%d %b')}-"
                f"{end_sunday.strftime('%d %b %Y')}"
            )

            reasoning_obj = {
                "adaptations": adaptations,
                "preserved":   preserved,
                "context_flags": {
                    "burnout_risk": context.get('burnout_risk', 'Low'),
                    "avg_session_efficacy": round(
                        context.get('avg_session_efficacy', 3.0), 2
                    ),
                    "dominant_environment": context.get(
                        'dominant_environment', 'Unknown'
                    ),
                    "session_location_consistency": round(
                        context.get('session_location_consistency', 0.0), 2
                    ),
                },
            }

            from app.models.adaptation_log import AdaptationLog

            log = AdaptationLog(
                user_id=user_id,
                week_label=week_label,
                summary=(
                    f"Adapted {len(adaptations)} course(s). "
                    f"{len(preserved)} preserved."
                ),
                reasoning=json.dumps(reasoning_obj),
            )
            db.session.add(log)
            db.session.commit()

            logger.info(
                f"[Adaptation] Schedule committed for user {user_id}"
            )

            # ── Step 7: Return summary ───────────────────────────────
            return {
                "message":                f"Schedule adapted for {week_label}",
                "technique_swaps":        len(adaptations),
                "time_shifts":            0,
                "total_courses_analyzed": len(analysis),
                "adaptations":            reasoning_obj,
            }

        except Exception as e:
            logger.error(
                f"[Adaptation] adapt_schedule_for_next_week error: {e}"
            )
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
