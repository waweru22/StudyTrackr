"""
seed_demo_users.py
==================
StudyTrackr demo user seeder. Run from the backend/ directory:

    python seed_demo_users.py

PREREQUISITES:
    1. inference_service.py template enforcement bug is fixed
    2. InferenceService.generate_week_schedule() accepts week_start_override param
    3. All course codes below exist in the Course table (verified against seed_courses data)

WHAT THIS SCRIPT PRODUCES:

    Ernest (ernestisabookworm_) — Level 300, Semester 2, Deep Work template
        • Courses: SEN306, CSC308, SEN304, SEN322, GST312
        • 1 week of session history (last week's dates)
        • SEN306 (OOAD, weight 4) causing problems: Low Energy, drained, won't repeat
        • CSC308 (OS) performing well
        • Ready for live Week 2 adaptation during defense demo

    Ameer (ameerreadsalot_) — Level 200, Semester 2, Pomodoro template
        • Courses: MTH202, IFT212, COS202, GST212, ENT212
        • 1 week of session history (last week's dates)
        • COS202 (Programming II, weight 3): Pomodoro interrupts coding flow
        • MTH202 (Math II, weight 5): thriving with Pomodoro
        • Ready to begin iterative seeding (Weeks 2 and 3 done with Claude's help)

ITERATIVE PROCESS FOR AMEER (after running this script):
    1. Log in as Ameer, go to Schedule, click Adapt Schedule
    2. Copy the generated Week 2 schedule (course + technique per block)
    3. Bring it to Claude — Claude writes the Week 2 session seed snippet
    4. Run that snippet → adapt again → Claude writes Week 3 sessions
    5. Seed Week 3 → Ameer is demo-ready with 3 weeks of real adaptation history
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User
from app.models.session import ScheduleBlock, StudySession
from app.models.course import Course
from app.services.inference_service import InferenceService
from app.services.gamification_service import GamificationService

# try:
#     from app.models.user_course import UserCourse
# except ImportError:
#     from app.models.user import UserCourse

app = create_app()


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

DEMO_PASSWORD = "1234567"

TODAY       = date.today()
THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())
LAST_MONDAY = THIS_MONDAY - timedelta(weeks=1)   # Week 1 anchored to last week

# ── Course codes — must match Course.code exactly (no spaces) ──────────────
# Level 300, Semester 2 — for Ernest
ERNEST_COURSES = ["SEN306", "CSC308", "SEN304", "SEN322", "GST312"]

# Level 200, Semester 2 — for Ameer
AMEER_COURSES = ["MTH202", "IFT212", "COS202", "GST212", "ENT212"]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clean_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        StudySession.query.filter_by(user_id=user.id).delete()
        ScheduleBlock.query.filter_by(user_id=user.id).delete()
        try:
            from app.models.adaptation_log import AdaptationLog
            AdaptationLog.query.filter_by(user_id=user.id).delete()
        except Exception:
            pass
        try:
            UserCourse.query.filter_by(user_id=user.id).delete()
        except Exception:
            pass
        db.session.delete(user)
        db.session.commit()
        print(f"    Cleaned: {email}")


def enroll_courses(user, course_codes):
    courses = Course.query.filter(Course.code.in_(course_codes)).all()
    found   = [c.code for c in courses]
    missing = [c for c in course_codes if c not in found]
    if missing:
        print(f"    ⚠️  Course codes NOT found in DB: {missing}")
        print(f"    Enrolling in found only: {found}")
    for course in courses:
        if course not in user.courses:
            user.courses.append(course)
    db.session.commit()
    return courses


DEFAULT_SESSION = {
    "vibe":              "Normal",
    "social_setting":    "Solo",
    "learning_mode":     "Read/Write",
    "medium":            "Laptop/Slides",
    "environment":       "Library",
    "success_score":     3,
    "mood_after":        2,       # 1=Drained, 2=Neutral, 3=Energized
    "would_repeat":      True,
    "distraction_count": 0,
}


def seed_sessions(user_id, blocks, configs):
    """
    Creates a completed StudySession for every block.
    configs: dict keyed by course code, values override DEFAULT_SESSION.
    Courses not in configs receive neutral defaults.
    """
    if not blocks:
        print(f"    ⚠️  No blocks found (user {user_id})")
        return []

    created = []
    for block in blocks:
        code = block.course.code if block.course else "General"
        cfg  = {**DEFAULT_SESSION, **configs.get(code, {})}

        duration = int(
            (datetime.combine(block.date, block.end_time) -
             datetime.combine(block.date, block.start_time)).total_seconds() / 60
        )

        session = StudySession(
            user_id           = user_id,
            course_id         = block.course_id,
            start_time        = datetime.combine(block.date, block.start_time),
            end_time          = datetime.combine(block.date, block.end_time),
            duration_minutes  = duration,
            vibe              = cfg["vibe"],
            social_setting    = cfg["social_setting"],
            learning_mode     = cfg["learning_mode"],
            medium            = cfg["medium"],
            environment       = cfg["environment"],
            success_score     = cfg["success_score"],
            mood_after        = cfg["mood_after"],
            would_repeat      = cfg["would_repeat"],
            distraction_count = cfg["distraction_count"],
        )
        db.session.add(session)
        block.status = "completed"
        created.append(session)

    db.session.commit()

    for s in created:
        try:
            GamificationService.award_xp(user_id, s, s.distraction_count)
        except Exception as e:
            print(f"    ⚠️  XP award failed: {e}")

    print(f"    Sessions seeded: {len(created)}")
    return created


def get_upcoming_blocks(user_id):
    return ScheduleBlock.query.filter_by(user_id=user_id, status="upcoming").all()


# ─────────────────────────────────────────────────────────────────────────────
# ERNEST — 20221192@nileuniversity.edu.ng
# Level 300 | Semester 2 | Deep Work | 1 week done
#
# Courses:
#   SEN306  Object-Oriented Analysis and Design  weight 4  ← struggling
#   CSC308  Operating Systems                    weight 3  ← thriving
#   SEN304  Software Testing and QA              weight 2
#   SEN322  SE Innovation and New Tech           weight 2
#   GST312  Peace and Conflict Resolution        weight 2  ← easy
#
# Story:
#   SEN306 (OOAD) is complex design-heavy work — Deep Work sessions leave him
#   drained every time. Low Energy, never wants to repeat.
#   CSC308 (OS) is going really well with Deep Work in the mornings.
#
# What the engine should pick up during live demo:
#   → SEN306: low efficacy + burnout signal → technique change or load reduction
#   → CSC308: high efficacy → preserve
# ─────────────────────────────────────────────────────────────────────────────

def seed_ernest():
    print("\n  → Seeding Ernest (ernestisabookworm_)...")
    clean_user("20221192@nileuniversity.edu.ng")

    user = User(
        email                    = "20221192@nileuniversity.edu.ng",
        username                 = "ernestisabookworm_",
        hashed_password          = generate_password_hash(DEMO_PASSWORD),
        level                    = 300,
        base_template            = "deep_work_specialist",
        peak_time                = "morning",
        focus_threshold          = 90,
        learning_style           = "read_write",
        preferred_environment_v2 = "silent",
        study_mode               = "solo",
        daily_cognitive_budget   = 2,
        xp_points                = 310,
        badge                    = "Novice",
        streak_count             = 0,
        role                     = "student",
        is_verified              = True,
    )
    db.session.add(user)
    db.session.commit()

    enroll_courses(user, ERNEST_COURSES)

    print("    Generating Week 1 schedule (last week's dates)...")
    InferenceService.generate_week_schedule(user.id, week_start_override=THIS_MONDAY)

    blocks = get_upcoming_blocks(user.id)
    print(f"    Blocks generated: {len(blocks)}")

    configs = {
        # SEN306 (OOAD, weight 4): Deep Work is too heavy for design work.
        # Complex abstraction + long unbroken sessions = cognitive drain.
        # Three sessions of Low Energy + never repeats = clear burnout signal.
        "SEN306": {
            "vibe":              "Low Energy",
            "environment":       "Library",
            "success_score":     2,
            "mood_after":        1,       # Drained
            "would_repeat":      False,
            "distraction_count": 4,
        },
        # CSC308 (OS, weight 3): Deep Work in the morning works perfectly.
        # Technical, concept-heavy — benefits from long uninterrupted focus.
        "CSC308": {
            "vibe":              "High Energy",
            "environment":       "Library",
            "success_score":     5,
            "mood_after":        3,       # Energized
            "would_repeat":      True,
            "distraction_count": 0,
        },
        # SEN304 (Testing, weight 2): methodical work, average performance
        "SEN304": {
            "vibe":              "Normal",
            "environment":       "Library",
            "success_score":     3,
            "mood_after":        2,
            "would_repeat":      True,
            "distraction_count": 1,
        },
        # SEN322 (Innovation, weight 2): creative/discussion-based, slightly below average
        "SEN322": {
            "vibe":              "Normal",
            "environment":       "Library",
            "success_score":     3,
            "mood_after":        2,
            "would_repeat":      True,
            "distraction_count": 1,
        },
        # GST312 (Peace Studies, weight 2): light reading-based course, no issues
        "GST312": {
            "vibe":              "Normal",
            "environment":       "Library",
            "success_score":     4,
            "mood_after":        3,
            "would_repeat":      True,
            "distraction_count": 0,
        },
    }

    seed_sessions(user.id, blocks, configs)

    try:
        user.streak_count = GamificationService.calculate_streak(user.id)
        db.session.commit()
    except Exception as e:
        print(f"    ⚠️  Streak calculation failed: {e}")
    db.session.commit()

    print(f"    Streak: {user.streak_count} | XP: {user.xp_points} | Badge: {user.badge}")
    print("    ✓ Ernest ready — live demo: click Adapt to generate Week 2")
 

# ─────────────────────────────────────────────────────────────────────────────
# AMEER — 20220088@nileuniversity.edu.ng
# Level 200 | Semester 2 | Pomodoro (Balanced Sprinter) | 1 week done
#
# Courses:
#   MTH202  Mathematical Methods II              weight 5  ← thriving
#   IFT212  Computer Architecture & Organisation weight 4
#   COS202  Computer Programming II              weight 3  ← struggling
#   GST212  Philosophy, Logic & Human Existence  weight 2
#   ENT212  Entrepreneurship and Innovation      weight 2
#
# Story:
#   COS202 (Programming II): Pomodoro's 25-minute interruptions kill flow
#   when writing and debugging code. Student keeps losing context on problems.
#   Low scores, always drained, never wants to repeat.
#   MTH202: Pomodoro is perfect for maths — short focused problem sets
#   with built-in breaks. Thriving.
#
# What the engine should pick up on adaptation:
#   → COS202: low efficacy + drained → technique change (Feynman or longer blocks)
#   → MTH202: high efficacy → preserve Pomodoro
# ─────────────────────────────────────────────────────────────────────────────

def seed_ameer():
    print("\n  → Seeding Ameer (ameerreadsalot_)...")
    clean_user("20220088@nileuniversity.edu.ng")

    user = User(
        email                    = "20220088@nileuniversity.edu.ng",
        username                 = "ameerreadsalot_",
        hashed_password          = generate_password_hash(DEMO_PASSWORD),
        level                    = 200,
        base_template            = "balanced_sprinter",   # Pomodoro
        peak_time                = "morning",
        focus_threshold          = 25,
        learning_style           = "visual",
        preferred_environment_v2 = "silent",
        study_mode               = "solo",
        daily_cognitive_budget   = 3,
        xp_points                = 180,
        badge                    = "Novice",
        streak_count             = 0,
        role                     = "student",
        is_verified              = True,
    )
    db.session.add(user)
    db.session.commit()

    enroll_courses(user, AMEER_COURSES)

    print("    Generating Week 1 schedule (last week's dates)...")
    InferenceService.generate_week_schedule(user.id, week_start_override=THIS_MONDAY)

    blocks = get_upcoming_blocks(user.id)
    print(f"    Blocks generated: {len(blocks)}")

    configs = {
        # MTH202 (Math II, weight 5): Pomodoro is ideal.
        # Short focused sprints + breaks = exactly how maths revision works.
        "MTH202": {
            "vibe":              "High Energy",
            "environment":       "Library",
            "success_score":     5,
            "mood_after":        3,       # Energized
            "would_repeat":      True,
            "distraction_count": 0,
        },
        # IFT212 (Computer Architecture, weight 4): conceptual but manageable
        "IFT212": {
            "vibe":              "Normal",
            "environment":       "Library",
            "success_score":     3,
            "mood_after":        2,
            "would_repeat":      True,
            "distraction_count": 1,
        },
        # COS202 (Programming II, weight 3): Pomodoro kills the coding flow.
        # Every 25 minutes he has to stop mid-function, loses mental context.
        "COS202": {
            "vibe":              "Low Energy",
            "environment":       "Library",
            "success_score":     2,
            "mood_after":        1,       # Drained
            "would_repeat":      False,
            "distraction_count": 3,
        },
        # GST212 (Philosophy, weight 2): reading-heavy, perfectly fine
        "GST212": {
            "vibe":              "Normal",
            "environment":       "Library",
            "success_score":     4,
            "mood_after":        2,
            "would_repeat":      True,
            "distraction_count": 0,
        },
        # ENT212 (Entrepreneurship, weight 2): discussion-based, average
        "ENT212": {
            "vibe":              "Normal",
            "environment":       "Library",
            "success_score":     3,
            "mood_after":        2,
            "would_repeat":      True,
            "distraction_count": 1,
        },
    }

    seed_sessions(user.id, blocks, configs)

    try:
        user.streak_count = GamificationService.calculate_streak(user.id)
        db.session.commit()
    except Exception as e:
        print(f"    ⚠️  Streak calculation failed: {e}") 
    db.session.commit()

    print(f"    Streak: {user.streak_count} | XP: {user.xp_points} | Badge: {user.badge}")
    print("    ✓ Ameer ready — begin iterative seeding process")
    print("      Next: log in → Adapt Schedule → bring Week 2 schedule to Claude")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("StudyTrackr Demo Seeder")
    print("=" * 50)
    with app.app_context():
        seed_ernest()
        seed_ameer()
    print("\n" + "=" * 50)
    print("Done.\n")
    print("  Ernest | 20221192@nileuniversity.edu.ng | 1234567")
    print("  → Level 300 | Sem 2 | Deep Work | SEN306 struggling, CSC308 thriving\n")
    print("  Ameer  | 20220088@nileuniversity.edu.ng | 1234567")
    print("  → Level 200 | Sem 2 | Pomodoro  | COS202 struggling, MTH202 thriving\n")
    print("  Next for Ameer: adapt → bring Week 2 schedule to Claude → seed → repeat")