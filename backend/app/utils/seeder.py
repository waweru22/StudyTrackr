import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
StudyTrackr Master Seeder - PostgreSQL-safe
=============================================
Seeds ALL reference data the app needs to function:
  1. Courses (full Nile University SE curriculum)
  2. Knowledge base rules (expert system)
  3. Notification triggers
  4. Demo users: Ernest & Ameer

Safe to run multiple times (idempotent).
Run from backend/:  python -m app.utils.seeder
"""

from app import create_app, db
from werkzeug.security import generate_password_hash

app = create_app()


# =======================================================================
#  1. COURSES
# =======================================================================

def seed_courses():
    from app.models.course import Course

    courses = [
        # --- Weight 5: Critical Engineering & Logic ---
        {"code":"PHY101", "name":"General Physics I", "weight":5, "level":100, "semester":1, "credits":2},
        {"code":"PHY102", "name":"General Physics II", "weight":5, "level":100, "semester":2, "credits":2},
        {"code":"MTH201", "name":"Mathematical Methods I", "weight":5, "level":200, "semester":1, "credits":2},
        {"code":"MTH202", "name":"Mathematical Methods II", "weight":5, "level":200, "semester":2, "credits":2},
        {"code":"CSC203", "name":"Discrete Structures", "weight":5, "level":200, "semester":1, "credits":2},
        {"code":"CSC301", "name":"Data Structures", "weight":5, "level":300, "semester":1, "credits":3},
        {"code":"NUN-SEN405", "name":"Design and Analysis of Algorithms", "weight":5, "level":400, "semester":1, "credits":2},
        {"code":"NUN-SEN417", "name":"Compiler Construction", "weight":5, "level":400, "semester":1, "credits":2},
        {"code":"SEN441", "name":"Software Architecture and Design", "weight":5, "level":400, "semester":1, "credits":2},

        # --- Weight 4: High Complexity ---
        {"code":"MTH101", "name":"Elementary Mathematics I", "weight":4, "level":100, "semester":1, "credits":2},
        {"code":"MTH102", "name":"Elementary Mathematics II", "weight":4, "level":100, "semester":2, "credits":2},
        {"code":"IFT212", "name":"Computer Architecture and Organisation", "weight":4, "level":200, "semester":2, "credits":2},
        {"code":"NUN-DTS304", "name":"Database Management", "weight":4, "level":300, "semester":1, "credits":3},
        {"code":"NUN-IFT311", "name":"Web Application Development", "weight":4, "level":300, "semester":1, "credits":3},
        {"code":"NUN-SEN331", "name":"Engineering Mobile Application", "weight":4, "level":300, "semester":1, "credits":3},
        {"code":"SEN306", "name":"Object-Oriented Analysis and Design", "weight":4, "level":300, "semester":2, "credits":3},
        {"code":"NUN-CSC408", "name":"Artificial Intelligence", "weight":4, "level":400, "semester":2, "credits":3},
        {"code":"NUN-SEN444", "name":"Secure Code Development", "weight":4, "level":400, "semester":2, "credits":3},

        # --- Weight 3: Core Fundamentals ---
        {"code":"COS101", "name":"Introduction to Computing Sciences", "weight":3, "level":100, "semester":1, "credits":3},
        {"code":"COS102", "name":"Introduction to Problem Solving", "weight":3, "level":100, "semester":2, "credits":3},
        {"code":"SEN102", "name":"Introduction to Software Engineering", "weight":3, "level":100, "semester":2, "credits":2},
        {"code":"NUN-SEN207", "name":"Software Requirements and Design", "weight":3, "level":200, "semester":1, "credits":3},
        {"code":"COS201", "name":"Computer Programming I", "weight":3, "level":200, "semester":1, "credits":3},
        {"code":"COS202", "name":"Computer Programming II", "weight":3, "level":200, "semester":2, "credits":3},
        {"code":"NUN-SEN201", "name":"Introduction to Web Technologies", "weight":3, "level":200, "semester":1, "credits":3},
        {"code":"IFT211", "name":"Digital Logic Design", "weight":3, "level":200, "semester":1, "credits":2},
        {"code":"SEN301", "name":"Software Construction", "weight":3, "level":300, "semester":1, "credits":2},
        {"code":"NUN-ICT306", "name":"Data Communications and Network", "weight":3, "level":300, "semester":1, "credits":3},
        {"code":"CSC308", "name":"Operating Systems", "weight":3, "level":300, "semester":2, "credits":3},
        {"code":"NUN-SEN404", "name":"Software Reverse Engineering", "weight":3, "level":400, "semester":2, "credits":2},
        {"code":"NUN-SEN410", "name":"Human Computer Interaction", "weight":3, "level":400, "semester":2, "credits":3},

        # --- Weight 2: Process & methodology ---
        {"code":"NUN-SEN210", "name":"Software Engineering Process", "weight":2, "level":200, "semester":1, "credits":2},
        {"code":"GST212", "name":"Philosophy, Logic and Human Existence", "weight":2, "level":200, "semester":2, "credits":2},
        {"code":"ENT212", "name":"Entrepreneurship and Innovation", "weight":2, "level":200, "semester":2, "credits":2},
        {"code":"GST312", "name":"Peace and Conflict Resolution", "weight":2, "level":300, "semester":2, "credits":2},
        {"code":"ENT312", "name":"Venture Creation", "weight":2, "level":300, "semester":2, "credits":2},
        {"code":"SEN304", "name":"Software Testing and Quality Assurance", "weight":2, "level":300, "semester":2, "credits":2},
        {"code":"SEN322", "name":"Software Engineering Innovation and New Tech", "weight":2, "level":300, "semester":2, "credits":2},
        {"code":"COS409", "name":"Research Methodology & Tech Report", "weight":2, "level":400, "semester":1, "credits":3},
        {"code":"SEN401", "name":"Software Config Mgmt & Maintenance", "weight":2, "level":400, "semester":1, "credits":2},
        {"code":"INS401", "name":"Project Management", "weight":2, "level":400, "semester":1, "credits":2},
        {"code":"NUN-SEN407", "name":"Software Eng Professional Practice", "weight":2, "level":400, "semester":2, "credits":2},

        # --- Weight 1: General & Labs ---
        {"code":"GST111", "name":"Communication in English", "weight":1, "level":100, "semester":1, "credits":2},
        {"code":"NUN-GET101", "name":"Introduction to Engineering", "weight":1, "level":100, "semester":1, "credits":3},
        {"code":"PHY107", "name":"General Practical Physics I", "weight":1, "level":100, "semester":1, "credits":1},
        {"code":"STA111", "name":"Descriptive Statistics", "weight":1, "level":100, "semester":1, "credits":3},
        {"code":"NUN-COS103", "name":"Intro to AI and Machine Learning", "weight":1, "level":100, "semester":1, "credits":2},
        {"code":"GST112", "name":"Nigerian Peoples & Culture", "weight":1, "level":100, "semester":2, "credits":2},
        {"code":"NUN-COS112", "name":"Introduction to Green Technology", "weight":1, "level":100, "semester":2, "credits":2},
        {"code":"PHY108", "name":"General Practical Physics II", "weight":1, "level":100, "semester":2, "credits":1},
        {"code":"GST105", "name":"IT and Library Skills", "weight":1, "level":100, "semester":2, "credits":2},
        {"code":"NUN-COS204", "name":"Digital Media Communication", "weight":1, "level":200, "semester":2, "credits":2},
        {"code":"NUN-COS305", "name":"Remote Work and Collaboration", "weight":1, "level":300, "semester":1, "credits":2},
    ]

    added = 0
    for c_data in courses:
        if not Course.query.filter_by(code=c_data['code']).first():
            db.session.add(Course(**c_data))
            added += 1

    db.session.commit()
    print(f"  [OK] Courses: {added} added, {Course.query.count()} total")


# =======================================================================
#  2. KNOWLEDGE BASE (Expert System Rules)
# =======================================================================

def seed_knowledge():
    from app.models.course import StudyKnowledge

    tips = [
      {
        "principle": "Recall-Gated Consolidation",
        "rule_logic": "Exponential Signal-to-Noise Ratio (SNR) Improvement",
        "content": "Consistency in study environment acts as a filter for the long-term memory (LTM) system.",
        "inference_trigger": "If session_location_consistency > 0.8 AND course_weight >= 4, increase session_efficacy_multiplier by 1.5x.",
        "academic_source": "eLife (Recall-Gated Consolidation Theory, 2024)",
        "tags": "Environment, Exponential Growth, Consolidation",
        "rule_type": "schedule",
        "student_instruction": "Study this course in the same location every time. Your brain will begin to associate that environment with this subject, making recall faster and easier over time."
      },
      {
        "principle": "Desirable Difficulties (Interleaving)",
        "rule_logic": "Blocked-to-Interleaved Transition",
        "content": "For complex logic, initial learning should be 'blocked'. Once basic competency is reached, switch to 'Interleaved' scheduling.",
        "inference_trigger": "If cumulative_course_minutes > 180, modify schedule from 'Blocked' to 'Interleaved' for next 3 sessions.",
        "academic_source": "Bjork & Bjork (2011)",
        "tags": "Interleaving, Logic Transfer",
        "rule_type": "schedule",
        "student_instruction": "You have studied this subject enough to mix it up. In this session, alternate between this topic and a related one every 20 minutes instead of staying on one concept the whole time."
      },
      {
        "principle": "The Zeigarnik tactical Break",
        "rule_logic": "Interrupted Task Recall Enhancement",
        "content": "Incomplete tasks create higher mental tension and better recall.",
        "inference_trigger": "If session_vibe == 'High Frustration', trigger mandatory 'Distraction Log' (5-min) to activate Diffuse Mode.",
        "academic_source": "Dr. Barbara Oakley",
        "tags": "Breaks, Problem Solving",
        "rule_type": "session",
        "student_instruction": "You are feeling frustrated. Stop working on this problem right now. Take exactly 5 minutes away from your screen, then come back. Your brain will keep processing in the background."
      },
      {
        "principle": "The 2-3-5-7 Spaced Interval",
        "rule_logic": "Forgetting Curve Reset Algorithm",
        "content": "To counteract memory decay, info must be retrieved at strategic intervals.",
        "inference_trigger": "On Session_End(Success), auto-generate 'Review_Blocks' in schedule at T+1d, T+3d, and T+7d.",
        "academic_source": "Ebbinghaus / Cornell LSC",
        "tags": "Spaced Repetition, Algorithm",
        "rule_type": "schedule",
        "student_instruction": "This is a scheduled review session. Do not study new material. Instead, close your notes and try to recall everything you remember about the topic from your last session before checking."
      },
      {
        "principle": "The Focus Threshold Cap",
        "rule_logic": "Fatigue-Induced Error Prevention",
        "content": "Cognitive performance drops after the focus threshold.",
        "inference_trigger": "If current_session_duration > user_focus_threshold, trigger 'Mandatory Rest' state.",
        "academic_source": "Expert Systems with Applications (2023)",
        "tags": "Focus, Threshold",
        "rule_type": "session",
        "student_instruction": "You have hit your focus limit for this session. Stop now \u2014 continuing will result in pseudostudying where you are reading words but retaining nothing. Take a real break before your next block."
      },
      {
        "principle": "Behavioral Anchor Alignment",
        "rule_logic": "Circadian Rhythm Correction",
        "content": "Objective behavioral logs are prioritized over subjective onboarding data to ensure biological alignment.",
        "inference_trigger": "If weekly_audit_success_rate(actual_peak) > weekly_audit_success_rate(onboard_peak) by 20%, update student_profile.peak_time.",
        "academic_source": "Journal of Biological Rhythms (2022)",
        "tags": "Audit, Optimization",
        "rule_type": "schedule",
        "student_instruction": "Your actual performance data suggests your peak focus time may have shifted. This block has been moved to align with when you are historically most effective, not just what you said during setup."
      },
      {
        "principle": "The Feynman Technique",
        "rule_logic": "Deep Processing & Simplification",
        "content": "To learn deep concepts, teaching it in simple terms exposes gaps in understanding.",
        "inference_trigger": "If course_weight >= 4, suggest 'The Feynman Technique'.",
        "academic_source": "eLife (2024)",
        "tags": "Deep Work, Simplification",
        "rule_type": "schedule",
        "student_instruction": "Open a blank page or notebook. Write the topic at the top. Now explain it in simple language as if you are teaching it to someone who has never heard of it. Where you get stuck is exactly what you need to study next."
      },
      {
        "principle": "Pomodoro Technique",
        "rule_logic": "Time-Boxing for Focus",
        "content": "25 minutes intense focus, 5 minutes break.",
        "inference_trigger": "If course_weight <= 2, suggest 'Pomodoro' to maintain momentum.",
        "academic_source": "Cirillo (1980)",
        "tags": "Time Management, Focus",
        "rule_type": "schedule",
        "student_instruction": "Set a timer for 25 minutes. Work on this course and nothing else until it rings. Then stand up, move away from your desk, and rest for exactly 5 minutes. Repeat. Do not skip the break."
      },
      {
        "principle": "Blurting (Active Recall)",
        "rule_logic": "Retrieval Practice",
        "content": "Write down everything you know about a topic from memory, then check against notes.",
        "inference_trigger": "If course_weight == 3, suggest 'Blurting'.",
        "academic_source": "Roediger & Karpicke (2006)",
        "tags": "Active Recall, Memory",
        "rule_type": "schedule",
        "student_instruction": "Close your notes and every tab related to this topic. On a blank page, write down everything you can remember about it. Do not stop until you run out of ideas. Then open your notes and check what you missed."
      },
      {
        "principle": "Cognitive Load Balancing",
        "rule_logic": "Resource Depletion Management",
        "content": "Deep Work depletes cognitive resources faster. Budget constraints prevent burnout.",
        "inference_trigger": "If daily_cognitive_load > daily_cognitive_budget, reschedule overflow to next day.",
        "academic_source": "Sweller (1988)",
        "tags": "Cognitive Load, Budget",
        "rule_type": "schedule",
        "student_instruction": "Your schedule for today is heavy. This block has been kept shorter than usual to prevent cognitive overload. Focus only on the single most important concept for this course today, not the full topic."
      },
      {
        "principle": "Circadian Energy Mapping",
        "rule_logic": "Vibe-to-Complexity Alignment",
        "content": "High-complexity tasks should only be scheduled during 'High Energy' vibes.",
        "inference_trigger": "If session_vibe == 'Low Energy' AND course_weight >= 4, swap technique to 'Pomodoro' and limit duration to 25 mins.",
        "academic_source": "Biological Rhythm Research (2023)",
        "tags": "Vibe, Energy, Complexity",
        "rule_type": "session",
        "student_instruction": "Your energy is low right now. Do not attempt new or complex material. Use this time to review previously studied notes, rewrite summaries, or reorganise your study materials instead."
      },
      {
        "principle": "Environmental Contextualization",
        "rule_logic": "Location-Based Cognitive Load",
        "content": "Public environments increase auditory distractions. Solo/Deep Work techniques are less effective here.",
        "inference_trigger": "If session_environment in ['Class', 'Other'] AND social_setting == 'Group', prioritize 'Feynman Technique' (Peer Teaching mode).",
        "academic_source": "Environmental Psychology Review",
        "tags": "Environment, Social, Context",
        "rule_type": "session",
        "student_instruction": "You are in a social or noisy environment. Solo deep work will not be effective here. Instead, try explaining concepts out loud to whoever is nearby, or work through problems by talking them through as if teaching."
      },
      {
        "principle": "Template Enforcement (Deep Work)",
        "rule_logic": "Contiguous Block Allocation",
        "content": "The Deep Work template requires 90-120 minute uninterrupted blocks.",
        "inference_trigger": "If base_template == 'deep_work' AND course_weight >= 4, merge adjacent schedule slots into a single 120-min block.",
        "academic_source": "Cal Newport (Deep Work)",
        "tags": "Deep Work, Template",
        "rule_type": "schedule",
        "student_instruction": "This is an extended deep work block. Before you start, close every notification, put your phone in another room, and commit to zero interruptions for the full duration. The first 15 minutes may feel slow \u2014 push through it."
      },
    ]

    added, updated = 0, 0
    for t_data in tips:
        existing = StudyKnowledge.query.filter_by(principle=t_data['principle']).first()
        if existing:
            for key, val in t_data.items():
                setattr(existing, key, val)
            updated += 1
        else:
            db.session.add(StudyKnowledge(**t_data))
            added += 1

    db.session.commit()
    print(f"  [OK] Knowledge rules: {added} added, {updated} updated, {StudyKnowledge.query.count()} total")


# =======================================================================
#  3. NOTIFICATION TRIGGERS
# =======================================================================

def seed_notification_triggers():
    from app.models.notification_trigger import NotificationTrigger

    triggers = [
        {"trigger_name": "badge_earned", "description": "User earned a new badge by crossing an XP threshold", "is_active": True, "priority": "medium", "notification_type": "achievement", "send_push": True, "template_title": "Badge Earned! {badge_name}", "template_message": "You've reached {xp} XP and unlocked the {badge_name} badge. Great work!"},
        {"trigger_name": "burnout_warning", "description": "Detected 2+ low energy sessions in the last 3 sessions", "is_active": True, "priority": "urgent", "notification_type": "warning", "send_push": True, "template_title": "Burnout Detected", "template_message": "We noticed you've had low energy in recent sessions. Let's reduce your workload and take a break."},
        {"trigger_name": "streak_milestone", "description": "Streak reached 7, 14, 30, or 60 days", "is_active": True, "priority": "low", "notification_type": "achievement", "send_push": True, "template_title": "{streak}-Day Streak!", "template_message": "Amazing consistency! You've completed sessions for {streak} consecutive days."},
        {"trigger_name": "low_efficacy_session", "description": "Session completed with success_score < 2", "is_active": True, "priority": "low", "notification_type": "tip", "send_push": True, "template_title": "Session Didn't Go Well", "template_message": "That {course_name} session didn't feel productive (scored {score}/5). Try a different technique next time."},
        {"trigger_name": "missed_session", "description": "Scheduled block was not completed on time", "is_active": True, "priority": "medium", "notification_type": "warning", "send_push": True, "template_title": "You Missed a Session", "template_message": "You missed {course_name} at {time}. No worries - let's get back on track."},
        {"trigger_name": "course_struggling", "description": "Student consistently performing poorly in a course", "is_active": False, "priority": "low", "notification_type": "tip", "send_push": False, "template_title": "Struggling with {course_name}?", "template_message": "Your recent {course_name} sessions show low scores. Consider reviewing materials or trying a different study technique."},
        {"trigger_name": "peak_time_reminder", "description": "Reminder to study during identified peak productivity hours", "is_active": False, "priority": "low", "notification_type": "tip", "send_push": False, "template_title": "Peak Study Time", "template_message": "Your most productive study time is {peak_time}. Consider scheduling a session now."},
        {"trigger_name": "weekly_insights", "description": "Weekly summary of study performance and progress", "is_active": False, "priority": "low", "notification_type": "insight", "send_push": False, "template_title": "Your Weekly Study Insights", "template_message": "This week: {sessions_completed} sessions, {total_minutes} minutes studied, {avg_score} avg score."},
        {"trigger_name": "schedule_adapted", "description": "Schedule was automatically adjusted by the inference engine", "is_active": False, "priority": "medium", "notification_type": "insight", "send_push": False, "template_title": "Schedule Updated", "template_message": "Your study schedule has been adapted based on recent performance. Check your new blocks."},
        {"trigger_name": "long_gap_alert", "description": "Student has not studied for an extended period", "is_active": False, "priority": "low", "notification_type": "tip", "send_push": False, "template_title": "It's Been a While", "template_message": "You haven't had a study session in {days} days. A short session can help you get back on track."},
    ]

    added = 0
    for t_data in triggers:
        if not NotificationTrigger.query.filter_by(trigger_name=t_data['trigger_name']).first():
            db.session.add(NotificationTrigger(**t_data))
            added += 1

    db.session.commit()
    print(f"  [OK] Notification triggers: {added} added, {NotificationTrigger.query.count()} total")


# =======================================================================
#  4. DEMO USERS - Ernest & Ameer
# =======================================================================

DEMO_PASSWORD = "1234567"

def seed_demo_users():
    from app.models.user import User
    from app.models.course import Course

    # --- Ernest ---
    ernest_email = "20221192@nileuniversity.edu.ng"
    ernest = User.query.filter_by(email=ernest_email.lower()).first()
    if not ernest:
        ernest = User(
            username="ernestisabookworm_",
            email=ernest_email,
            hashed_password=generate_password_hash(DEMO_PASSWORD),
            level=300,
            role="student",
            is_verified=True,
            base_template="deep_work_specialist",
            peak_time="morning",
            focus_threshold=90,
            learning_style="read_write",
            preferred_environment_v2="silent",
            study_mode="solo",
            daily_cognitive_budget=2,
            xp_points=0,
            streak_count=0,
            badge="Novice",
        )
        db.session.add(ernest)
        db.session.flush()

        ernest_codes = ["SEN306", "CSC308", "SEN304", "SEN322", "GST312"]
        courses = Course.query.filter(Course.code.in_(ernest_codes)).all()
        for course in courses:
            if course not in ernest.courses:
                ernest.courses.append(course)

        db.session.commit()
        print(f"  [OK] Ernest created: {ernest_email}")
    else:
        print(f"  [SKIP] Ernest already exists: {ernest_email}")

    # --- Ameer ---
    ameer_email = "20220088@nileuniversity.edu.ng"
    ameer = User.query.filter_by(email=ameer_email.lower()).first()
    if not ameer:
        ameer = User(
            username="ameerreadsalot_",
            email=ameer_email,
            hashed_password=generate_password_hash(DEMO_PASSWORD),
            level=200,
            role="student",
            is_verified=True,
            base_template="balanced_sprinter",
            peak_time="morning",
            focus_threshold=25,
            learning_style="visual",
            preferred_environment_v2="silent",
            study_mode="solo",
            daily_cognitive_budget=3,
            xp_points=0,
            streak_count=0,
            badge="Novice",
        )
        db.session.add(ameer)
        db.session.flush()

        ameer_codes = ["MTH202", "IFT212", "COS202", "GST212", "ENT212"]
        courses = Course.query.filter(Course.code.in_(ameer_codes)).all()
        for course in courses:
            if course not in ameer.courses:
                ameer.courses.append(course)

        db.session.commit()
        print(f"  [OK] Ameer created: {ameer_email}")
    else:
        print(f"  [SKIP] Ameer already exists: {ameer_email}")


# =======================================================================
#  5. VERIFICATION
# =======================================================================

def verify_seed():
    from app.models.course import Course, StudyKnowledge
    from app.models.user import User
    from app.models.notification_trigger import NotificationTrigger

    print("\n--- Seed Verification ---")
    print(f"Courses:              {Course.query.count()}")
    print(f"Knowledge base rules: {StudyKnowledge.query.count()}")
    print(f"Notification triggers:{NotificationTrigger.query.count()}")
    print(f"Users:                {User.query.count()}")

    ernest = User.query.filter_by(email='20221192@nileuniversity.edu.ng').first()
    ameer = User.query.filter_by(email='20220088@nileuniversity.edu.ng').first()

    print(f"Ernest exists:        {'[OK]' if ernest else '[FAIL] MISSING'}")
    print(f"Ameer exists:         {'[OK]' if ameer else '[FAIL] MISSING'}")

    if ernest:
        print(f"Ernest courses:       {len(ernest.courses)}")
    if ameer:
        print(f"Ameer courses:        {len(ameer.courses)}")
    print("--- End Verification ---\n")


# =======================================================================
#  MAIN
# =======================================================================

def run_seeder():
    print("\n========================================")
    print("|   StudyTrackr Master Seeder          |")
    print("========================================\n")

    # 1. Courses
    try:
        seed_courses()
    except Exception as e:
        db.session.rollback()
        print(f"  [FAIL] Courses seeding failed: {e}")

    # 2. Knowledge base rules
    try:
        seed_knowledge()
    except Exception as e:
        db.session.rollback()
        print(f"  [FAIL] Knowledge seeding failed: {e}")

    # 3. Notification triggers
    try:
        seed_notification_triggers()
    except Exception as e:
        db.session.rollback()
        print(f"  [FAIL] Notification triggers seeding failed: {e}")

    # 4. Demo users
    try:
        seed_demo_users()
    except Exception as e:
        db.session.rollback()
        print(f"  [FAIL] Demo user seeding failed: {e}")

    # 5. Verify
    verify_seed()

    print("Seeding complete.\n")


if __name__ == '__main__':
    with app.app_context():
        run_seeder()