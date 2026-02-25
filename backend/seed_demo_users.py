"""
StudyTrackr Demo User Seeding Script
=====================================
Run from your backend root with:
    python seed_demo_users.py

Or from Flask shell:
    flask shell
    exec(open('seed_demo_users.py').read())

Creates two demo users:
  - demo_user2@nileuni.edu.ng  (Developing — 1-2 weeks in)
  - demo_user3@nileuni.edu.ng  (Mature — 4+ weeks in)

Password for both: StudyTrackr2025!
"""

import os
import sys
from datetime import datetime, timedelta, date, time, timezone

# ── Bootstrap Flask app context if running as standalone script ──────────────
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import create_app, db
    app = create_app()
    ctx = app.app_context()
    ctx.push()
else:
    from app import db

from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.session import StudySession, ScheduleBlock
from app.models.course import Course


# ── Helpers ──────────────────────────────────────────────────────────────────

LAGOS = timezone(timedelta(hours=1))

def days_ago(n, hour=10, minute=0):
    """Return a timezone-aware datetime N days ago at the given hour."""
    d = datetime.now(LAGOS) - timedelta(days=n)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0)


def make_session(user_id, course_id, days_back, start_hour,
                 vibe, environment, success_score,
                 distraction_count, mood_after, would_repeat,
                 duration_minutes, learning_mode='Read/Write'):
    """Create and return a StudySession object (not yet added to db.session)."""
    start = days_ago(days_back, start_hour)
    end = start + timedelta(minutes=duration_minutes)
    return StudySession(
        user_id=user_id,
        course_id=course_id,
        start_time=start,
        end_time=end,
        vibe=vibe,
        environment=environment,
        success_score=success_score,
        distraction_count=distraction_count,
        mood_after=mood_after,
        would_repeat=would_repeat,
        duration_minutes=duration_minutes,
        learning_mode=learning_mode,
        social_setting='Solo',
        session_goal='Complete study block',
    )


def get_courses(level):
    """Return up to 6 courses at the given level."""
    courses = Course.query.filter_by(level=level).limit(6).all()
    if not courses:
        raise RuntimeError(
            f"No courses found for level {level}. "
            "Make sure your course seeder has run first."
        )
    return courses


def clear_user(email):
    """Remove an existing demo user and all their data."""
    user = User.query.filter_by(email=email).first()
    if user:
        StudySession.query.filter_by(user_id=user.id).delete()
        ScheduleBlock.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        print(f"  Cleared existing user: {email}")


# ════════════════════════════════════════════════════════════════════════════
#  USER 2 — DEVELOPING  (Balanced Sprinter / Pomodoro, Level 300)
#  8-10 sessions over ~2 weeks. Mixed results. Burnout risk triggered.
# ════════════════════════════════════════════════════════════════════════════

def seed_user2():
    print("\n── Seeding User 2 (Developing) ──")
    EMAIL = 'demo_user2@nileuni.edu.ng'
    clear_user(EMAIL)

    user = User(
        username='ada_learns',
        email=EMAIL,
        hashed_password=generate_password_hash('StudyTrackr2025!'),
        level=300,
        role='student',
        base_template='sprinter',          # Balanced Sprinter (Pomodoro)
        peak_time='morning',
        focus_threshold=60,
        daily_cognitive_budget=3,
        learning_style='read_write',
        preferred_environment_v2='silent',
        study_mode='alone',
        xp_points=0,
        streak_count=0,
        badge='Novice',
    )
    db.session.add(user)
    db.session.flush()  # get user.id

    courses = get_courses(300)
    c = [course.id for course in courses]  # shorthand list of course IDs

    # ── 10 sessions over the past 14 days ────────────────────────────────
    # Pattern: Library = high scores, Home = low/mixed, 2 Low Energy vibes
    # Last 3 sessions: Low Energy × 2 → triggers burnout_risk = 'High'
    sessions_data = [
        # (days_back, hour, vibe,         environment, score, distractions, mood, repeat, duration)
        (14, 8,  'High Energy', 'Library', 5, 0, 3, True,  50),   # great start
        (13, 9,  'Normal',      'Library', 4, 1, 2, True,  50),   # solid
        (12, 8,  'High Energy', 'Library', 4, 0, 3, True,  45),   # good
        (11, 10, 'Normal',      'Home',    3, 2, 2, False, 50),   # home = distracted
        (10, 9,  'High Energy', 'Library', 4, 1, 2, True,  50),   # bounce back
        (8,  8,  'Normal',      'Library', 4, 1, 2, True,  45),   # decent
        (7,  11, 'Normal',      'Home',    2, 2, 1, False, 35),   # home = poor
        (5,  8,  'Low Energy',  'Home',    2, 2, 1, False, 35),   # burnout starts
        (4,  9,  'Low Energy',  'Home',    2, 2, 1, False, 25),   # burnout continues
        (3,  8,  'Low Energy',  'Library', 2, 1, 2, False, 35),   # still low
    ]

    total_xp = 0
    for i, (days_back, hour, vibe, env, score,
            distractions, mood, repeat, dur) in enumerate(sessions_data):
        s = make_session(
            user_id=user.id,
            course_id=c[i % len(c)],
            days_back=days_back,
            start_hour=hour,
            vibe=vibe,
            environment=env,
            success_score=score,
            distraction_count=distractions,
            mood_after=mood,
            would_repeat=repeat,
            duration_minutes=dur,
        )
        db.session.add(s)
        # XP: (duration / 90) * 100 - (distractions * 10)
        xp = max(0, int((dur / 90.0) * 100 - distractions * 10))
        total_xp += xp

    # Streak: last 5 consecutive days (days 1-5 back from today)
    # We have sessions at days 3, 4, 5 — add two more for days 1 and 2
    for days_back in [2, 1]:
        s = make_session(
            user_id=user.id,
            course_id=c[0],
            days_back=days_back,
            start_hour=8,
            vibe='Normal',
            environment='Library',
            success_score=3,
            distraction_count=1,
            mood_after=2,
            would_repeat=True,
            duration_minutes=50,
        )
        db.session.add(s)
        total_xp += max(0, int((50 / 90.0) * 100 - 10))

    user.xp_points = total_xp
    user.streak_count = 5
    user.badge = 'Novice'

    # Add courses to user
    user.courses.extend(courses)

    db.session.commit()

    # Force created_at override after commit (bypasses server_default)
    db.session.execute(
        db.text("UPDATE \"user\" SET created_at = :d WHERE id = :id"),
        {"d": datetime.now(LAGOS) - timedelta(days=14), "id": user.id}
    )
    db.session.commit()

    # Generate schedule (after commit so courses are linked)
    from app.services.inference_service import InferenceService
    InferenceService.generate_week_schedule(user.id)

    print(f"  ✓ User 2 created: {EMAIL}")
    print(f"    Joined: {(datetime.now(LAGOS) - timedelta(days=14)).strftime('%Y-%m-%d')} (14 days ago)")
    print(f"    XP: {user.xp_points} | Streak: {user.streak_count} | Badge: {user.badge}")
    print(f"    Sessions: {len(sessions_data) + 2} | Template: {user.base_template}")
    print(
        "    Expected: burnout_risk=High (3× Low Energy), "
        "reduced blocks, dip in Focus Pulse"
    )


# ════════════════════════════════════════════════════════════════════════════
#  USER 3 — MATURE  (Deep-Work Specialist, Level 400)
#  25 sessions over ~5 weeks. Clear pattern: Library morning = best.
#  XP > 1000 → Apprentice badge. Streak 18 days.
# ════════════════════════════════════════════════════════════════════════════

def seed_user3():
    print("\n── Seeding User 3 (Mature) ──")
    EMAIL = 'demo_user3@nileuni.edu.ng'
    clear_user(EMAIL)

    user = User(
        username='chidi_masters',
        email=EMAIL,
        hashed_password=generate_password_hash('StudyTrackr2025!'),
        level=400,
        role='student',
        base_template='deepwork',          # Deep-Work Specialist
        peak_time='morning',
        focus_threshold=110,               # Intense (90m-2hrs)
        daily_cognitive_budget=4,
        learning_style='read_write',
        preferred_environment_v2='silent',
        study_mode='alone',
        xp_points=0,
        streak_count=0,
        badge='Novice',
    )
    db.session.add(user)
    db.session.flush()

    courses = get_courses(400)
    c = [course.id for course in courses]

    # ── 25 sessions over 35 days ──────────────────────────────────────────
    # Clear pattern: Library morning = 4.0-5.0, Home afternoon = 1.5-2.5
    # Upward trend overall → Focus Pulse shows recovery and growth
    sessions_data = [
        # Week 1 — establishing baseline (mixed)
        (35, 8,  'Normal',      'Library',   4, 1, 2, True,  90),
        (34, 14, 'Normal',      'Home',       2, 2, 1, False, 60),
        (33, 8,  'High Energy', 'Library',   4, 0, 3, True,  90),
        (32, 9,  'Normal',      'Library',   4, 1, 2, True,  90),
        (31, 15, 'Low Energy',  'Home',       2, 2, 1, False, 45),

        # Week 2 — pattern emerging
        (28, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (27, 8,  'High Energy', 'Library',   4, 0, 3, True,  90),
        (26, 14, 'Normal',      'Home',       2, 2, 1, False, 60),
        (25, 8,  'Normal',      'Library',   4, 1, 2, True,  90),
        (24, 9,  'High Energy', 'Library',   5, 0, 3, True,  110),

        # Week 3 — system adapting, mostly Library mornings
        (21, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (20, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (19, 8,  'Normal',      'Library',   4, 1, 2, True,  90),
        (18, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (17, 14, 'Low Energy',  'Home',       2, 2, 1, False, 45),

        # Week 4 — mature phase, strong consistency
        (14, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (13, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (12, 8,  'Normal',      'Library',   4, 1, 2, True,  90),
        (11, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (10, 8,  'High Energy', 'Library',   5, 0, 3, True,  110),

        # Week 5 — peak performance streak
        (7,  8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (6,  8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (5,  8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (4,  8,  'High Energy', 'Library',   5, 0, 3, True,  110),
        (3,  8,  'High Energy', 'Library',   5, 0, 3, True,  110),
    ]

    total_xp = 0
    for i, (days_back, hour, vibe, env, score,
            distractions, mood, repeat, dur) in enumerate(sessions_data):
        s = make_session(
            user_id=user.id,
            course_id=c[i % len(c)],
            days_back=days_back,
            start_hour=hour,
            vibe=vibe,
            environment=env,
            success_score=score,
            distraction_count=distractions,
            mood_after=mood,
            would_repeat=repeat,
            duration_minutes=dur,
        )
        db.session.add(s)
        xp = max(0, int((dur / 90.0) * 100 - distractions * 10))
        total_xp += xp

    # Extend streak: add sessions for days 2 and 1
    for days_back in [2, 1]:
        s = make_session(
            user_id=user.id,
            course_id=c[0],
            days_back=days_back,
            start_hour=8,
            vibe='High Energy',
            environment='Library',
            success_score=5,
            distraction_count=0,
            mood_after=3,
            would_repeat=True,
            duration_minutes=110,
        )
        db.session.add(s)
        total_xp += int((110 / 90.0) * 100)

    user.xp_points = total_xp
    user.streak_count = 18
    user.badge = 'Apprentice' if total_xp >= 1000 else 'Novice'

    user.courses.extend(courses)
    db.session.commit()

    # Force created_at override after commit (bypasses server_default)
    db.session.execute(
        db.text("UPDATE \"user\" SET created_at = :d WHERE id = :id"),
        {"d": datetime.now(LAGOS) - timedelta(days=35), "id": user.id}
    )
    db.session.commit()

    from app.services.inference_service import InferenceService
    InferenceService.generate_week_schedule(user.id)

    print(f"  ✓ User 3 created: {EMAIL}")
    print(f"    Joined: {(datetime.now(LAGOS) - timedelta(days=35)).strftime('%Y-%m-%d')} (35 days ago)")
    print(f"    XP: {user.xp_points} | Streak: {user.streak_count} | Badge: {user.badge}")
    print(f"    Sessions: {len(sessions_data) + 2} | Template: {user.base_template}")
    print(
        "    Expected: dominant_environment=Library, avg_efficacy high, "
        "Feynman + Deep Work blocks, upward Focus Pulse"
    )


# ════════════════════════════════════════════════════════════════════════════
#  SUMMARY TABLE
# ════════════════════════════════════════════════════════════════════════════

def print_summary():
    print("\n" + "═" * 60)
    print("  DEMO USER CREDENTIALS")
    print("═" * 60)
    print("  User 2 (Developing):")
    print("    Email:    demo_user2@nileuni.edu.ng")
    print("    Password: StudyTrackr2025!")
    print("    Joined:   14 days ago")
    print("    Story:    2 weeks in, burnout risk triggered,")
    print("              mixed Library/Home performance")
    print()
    print("  User 3 (Mature):")
    print("    Email:    demo_user3@nileuni.edu.ng")
    print("    Password: StudyTrackr2025!")
    print("    Joined:   35 days ago")
    print("    Story:    5 weeks in, Library mornings dominate,")
    print("              Apprentice badge, 18-day streak")
    print("═" * 60)
    print("\n  Demo flow:")
    print("  1. Register live → cold start schedule (User 1)")
    print("  2. Login as User 2 → show adaptation beginning")
    print("  3. Login as User 3 → show mature personalisation")
    print("  4. Complete a live session as User 2 → regenerate")
    print()


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Starting demo user seeding...")
    try:
        seed_user2()
        seed_user3()
        print_summary()
        print("✓ Seeding complete.")
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'ctx' in dir():
            ctx.pop()