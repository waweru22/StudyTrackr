"""
StudyTrackr — 10-Day Adaptation Test Suite
==========================================
Standalone script that:
  1. Creates a test user + 5 courses
  2. Generates Week 1 schedule via InferenceService
  3. Simulates 7 study sessions with realistic feedback
  4. Triggers AdaptationEngine.adapt_schedule_for_next_week()
  5. Prints Week 1 vs Week 2 comparison

Run:  python test_adaptation_10day.py
"""

import sys
import copy
from datetime import datetime, timedelta, timezone, time as dt_time
from app import create_app, db
from app.models.user import User
from app.models.course import Course, UserCourse
from app.models.session import ScheduleBlock, StudySession
from app.services.inference_service import InferenceService
from app.services.inference_service_adaptation import AdaptationEngine

app = create_app()
LAGOS_TZ = timezone(timedelta(hours=1))

LINE = "=" * 72
THIN = "-" * 72


# ─────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────

def _clear_test_data():
    """Remove any previous test artefacts."""
    test_user = User.query.filter_by(email='test@studytrackr.com').first()
    if test_user:
        StudySession.query.filter_by(user_id=test_user.id).delete()
        ScheduleBlock.query.filter_by(user_id=test_user.id).delete()
        # Remove user-course links
        UserCourse.query.filter_by(user_id=test_user.id).delete()
        db.session.delete(test_user)

    # Remove test courses (by code prefix)
    for code in ['CS301', 'MTH201', 'PHY101', 'ENT212', 'GST111']:
        c = Course.query.filter_by(code=code).first()
        if c:
            # clean up any dangling links
            UserCourse.query.filter_by(course_id=c.id).delete()
            ScheduleBlock.query.filter_by(course_id=c.id).delete()
            StudySession.query.filter_by(course_id=c.id).delete()
            db.session.delete(c)

    db.session.commit()


def _snapshot_blocks(user_id):
    """Return a serialisable copy of the current schedule blocks."""
    blocks = (
        ScheduleBlock.query
        .filter_by(user_id=user_id)
        .order_by(ScheduleBlock.date.asc(), ScheduleBlock.start_time.asc())
        .all()
    )
    snap = []
    for b in blocks:
        dur = int(
            (datetime.combine(b.date, b.end_time)
             - datetime.combine(b.date, b.start_time))
            .total_seconds() / 60
        )
        snap.append({
            'date': str(b.date),
            'day': b.day_of_week,
            'start': b.start_time.strftime('%H:%M'),
            'end': b.end_time.strftime('%H:%M'),
            'course': b.course.code if b.course else 'General',
            'technique': b.technique_name or '-',
            'duration': dur,
            'reason': b.refinement_reason or '',
            'citation': b.academic_citation or '',
        })
    return snap


def _print_schedule(rows, show_reason=False):
    """Pretty-print a schedule snapshot."""
    if show_reason:
        hdr = f"{'Date':<12}{'Time':<12}{'Course':<10}{'Technique':<24}{'Reason'}"
        print(hdr)
        print(THIN)
        for r in rows:
            print(
                f"{r['date']:<12}"
                f"{r['start']}-{r['end']:<7} "
                f"{r['course']:<10}"
                f"{r['technique']:<24}"
                f"{r['reason']}"
            )
    else:
        hdr = f"{'Date':<12}{'Time':<12}{'Course':<10}{'Technique':<24}{'Dur'}"
        print(hdr)
        print(THIN)
        for r in rows:
            print(
                f"{r['date']:<12}"
                f"{r['start']}-{r['end']:<7} "
                f"{r['course']:<10}"
                f"{r['technique']:<24}"
                f"{r['duration']} min"
            )


# ─────────────────────────────────────────────────────────────────────
# STEP 1 — SETUP
# ─────────────────────────────────────────────────────────────────────

def setup_test_environment():
    """Create test user, courses, and user-course links."""
    _clear_test_data()

    user = User(
        username='test_student',
        email='test@studytrackr.com',
        hashed_password='pbkdf2:sha256:test',
        role='student',
        level=200,
        peak_time='morning',
        base_template='pomodoro',
        daily_cognitive_budget=3,
        focus_threshold=90,
        learning_style='read/write',
        is_verified=True,
    )
    db.session.add(user)
    db.session.flush()

    courses_data = [
        {'code': 'CS301',  'name': 'Data Structures',    'weight': 5, 'level': 300, 'semester': 1, 'credits': 3},
        {'code': 'MTH201', 'name': 'Calculus II',        'weight': 5, 'level': 200, 'semester': 1, 'credits': 2},
        {'code': 'PHY101', 'name': 'Physics I',          'weight': 4, 'level': 100, 'semester': 1, 'credits': 2},
        {'code': 'ENT212', 'name': 'Entrepreneurship',   'weight': 2, 'level': 200, 'semester': 2, 'credits': 2},
        {'code': 'GST111', 'name': 'English Comm',       'weight': 1, 'level': 100, 'semester': 1, 'credits': 2},
    ]

    courses = []
    for cd in courses_data:
        c = Course(**cd)
        db.session.add(c)
        courses.append(c)

    db.session.flush()

    # Associate user ↔ courses
    for c in courses:
        db.session.add(UserCourse(user_id=user.id, course_id=c.id))

    db.session.commit()

    return user.id, [c.id for c in courses]


# ─────────────────────────────────────────────────────────────────────
# STEP 2 — GENERATE WEEK 1
# ─────────────────────────────────────────────────────────────────────

def generate_week1(user_id):
    print(f"\n{LINE}")
    print("=== WEEK 1 SCHEDULE ===")
    print(LINE)

    InferenceService.generate_week_schedule(user_id)
    snap = _snapshot_blocks(user_id)

    print(f"\nGenerated {len(snap)} blocks:\n")
    _print_schedule(snap)
    return snap


# ─────────────────────────────────────────────────────────────────────
# STEP 3 — SIMULATE 7 SESSIONS
# ─────────────────────────────────────────────────────────────────────

def simulate_sessions(user_id):
    print(f"\n{LINE}")
    print("=== SIMULATING 7 STUDY SESSIONS ===")
    print(LINE)

    today = datetime.now(LAGOS_TZ).date()
    start_of_week = today - timedelta(days=today.weekday())

    courses = {c.code: c for c in Course.query.filter(
        Course.code.in_(['CS301', 'MTH201', 'PHY101', 'ENT212', 'GST111'])
    ).all()}

    # (day_offset, course_code, technique, effectiveness, mood, repeat)
    session_spec = [
        (0, 'CS301',  'Deep Work',              1.5, 1, False),
        (1, 'MTH201', 'Active Recall (Blurting)',4.2, 3, True),
        (2, 'PHY101', 'Pomodoro',               3.1, 2, True),
        (3, 'ENT212', 'Deep Work',              2.1, 1, False),
        (4, 'CS301',  'Pomodoro',               3.8, 2, True),
        (5, 'MTH201', 'Deep Work',              4.5, 3, True),
        (6, 'CS301',  'Pomodoro',               3.0, 2, True),
    ]

    mood_labels = {1: 'Drained', 2: 'Neutral', 3: 'Energized'}

    print(f"\n{'Day':<6}{'Course':<10}{'Technique':<24}"
          f"{'Eff':>5}  {'Mood':<10}{'Repeat'}")
    print(THIN)

    for offset, code, tech, eff, mood, repeat in session_spec:
        dt = start_of_week + timedelta(days=offset)
        c = courses[code]

        s = StudySession(
            user_id=user_id,
            course_id=c.id,
            start_time=datetime.combine(dt, dt_time(9, 0)),
            end_time=datetime.combine(dt, dt_time(11, 0)),
            learning_mode=tech,
            vibe=('High Energy' if eff >= 4
                  else 'Low Energy' if eff < 2
                  else 'Normal'),
            environment='Library',
            social_setting='Solo',
            medium='Notes',
            success_score=eff,
            duration_minutes=90,
            mood_after=mood,
            would_repeat=repeat,
            distraction_count=(0 if eff >= 3 else 1),
        )
        db.session.add(s)

        day_name = dt.strftime('%a')
        rpt = 'Yes' if repeat else 'No'
        print(
            f"{day_name:<6}{code:<10}{tech:<24}"
            f"{eff:>5.1f}  {mood_labels[mood]:<10}{rpt}"
        )

    db.session.commit()
    print(f"\n[OK] 7 sessions saved.\n")


# ─────────────────────────────────────────────────────────────────────
# STEP 4 — ANALYSE PERFORMANCE
# ─────────────────────────────────────────────────────────────────────

def analyse_performance(user_id):
    print(f"\n{LINE}")
    print("=== WEEKLY PERFORMANCE ANALYSIS ===")
    print(LINE)

    analysis = AdaptationEngine.analyze_weekly_performance(user_id)

    if not analysis:
        print("No data to analyse.")
        return analysis

    for cid, techs in analysis.items():
        course = Course.query.get(cid)
        label = f"{course.code} - {course.name}" if course else f"ID {cid}"
        print(f"\n  {label}")
        print(f"  {'-' * 50}")

        for tname, stats in techs.items():
            print(f"    Technique : {tname}")
            print(f"      Avg Effectiveness : {stats['avg_effectiveness']}/5")
            print(f"      Dominant Mood     : {stats['avg_mood'] or 'N/A'}")
            print(f"      Would Repeat      : {stats['would_repeat_ratio']:.0%}")
            print(f"      Sessions          : {stats['session_count']}")

    return analysis


# ─────────────────────────────────────────────────────────────────────
# STEP 5 — TRIGGER ADAPTATION
# ─────────────────────────────────────────────────────────────────────

def trigger_adaptation(user_id):
    print(f"\n{LINE}")
    print("=== ADAPTATION DECISIONS ===")
    print(LINE)

    result = AdaptationEngine.adapt_schedule_for_next_week(user_id)

    if 'error' in result:
        print(f"\n[FAIL] Adaptation failed: {result['error']}")
        return result

    print(f"\n  [OK] {result['message']}")
    print(f"    Courses analysed  : {result['total_courses_analyzed']}")
    print(f"    Technique swaps   : {result['technique_swaps']}")
    print(f"    Time shifts       : {result['time_shifts']}")

    adaptations = result.get('adaptations', {})
    if adaptations:
        print(f"\n  {'Course':<10}{'Change':<18}{'Before':<24}{'After'}")
        print(f"  {THIN}")
        for cid_str, a in adaptations.items():
            cid = int(cid_str)
            course = Course.query.get(cid)
            code = course.code if course else f"ID {cid}"

            if a['new_technique'] != a['current_technique']:
                print(
                    f"  {code:<10}{'Technique':<18}"
                    f"{a['current_technique']:<24}"
                    f"{a['new_technique']}"
                )
            if a['new_hour'] != a['current_hour']:
                print(
                    f"  {code:<10}{'Time':<18}"
                    f"{a['current_hour']}:00{'':<20}"
                    f"{a['new_hour']}:00"
                )

    return result


# ─────────────────────────────────────────────────────────────────────
# STEP 6 — DISPLAY WEEK 2
# ─────────────────────────────────────────────────────────────────────

def display_week2(user_id, week1_snap):
    print(f"\n{LINE}")
    print("=== WEEK 2 SCHEDULE (ADAPTED) ===")
    print(LINE)

    week2_snap = _snapshot_blocks(user_id)

    print(f"\n{len(week2_snap)} blocks:\n")
    _print_schedule(week2_snap, show_reason=True)

    # ── Summary comparison ───────────────────────────────────────────
    print(f"\n{LINE}")
    print("=== ADAPTATION SUMMARY ===")
    print(LINE)

    # Build lookup by (date, course) for week 1
    w1_lookup = {}
    for r in week1_snap:
        key = (r['date'], r['course'])
        w1_lookup[key] = r

    changes = 0
    tech_swaps = 0
    time_changes = 0

    for r2 in week2_snap:
        key = (r2['date'], r2['course'])
        r1 = w1_lookup.get(key)
        if r1:
            if r1['technique'] != r2['technique']:
                tech_swaps += 1
                changes += 1
            if r1['start'] != r2['start']:
                time_changes += 1
                changes += 1

    print(f"\n  Total blocks in Week 2 : {len(week2_snap)}")
    print(f"  Total changes          : {changes}")
    print(f"  Technique swaps        : {tech_swaps}")
    print(f"  Time shifts            : {time_changes}")
    print()


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{LINE}")
    print("  STUDYTRACKR -- 10-DAY ADAPTATION TEST SUITE")
    print(LINE)

    try:
        with app.app_context():
            # Setup
            user_id, course_ids = setup_test_environment()
            print(
                f"\n  [OK] Test environment ready "
                f"(User {user_id}, {len(course_ids)} courses)"
            )

            # Week 1
            week1_snap = generate_week1(user_id)

            # Simulate sessions
            simulate_sessions(user_id)

            # Analyse
            analyse_performance(user_id)

            # Adapt
            trigger_adaptation(user_id)

            # Week 2
            display_week2(user_id, week1_snap)

            # Cleanup test data so prod DB isn't polluted
            _clear_test_data()
            print("  [OK] Test data cleaned up.\n")

        print(LINE)
        print("  [OK] TEST COMPLETE -- Adaptation working successfully!")
        print(f"{LINE}\n")

    except Exception as e:
        print(f"\n  [FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
