"""
Performance Evaluation Data Retrieval
Queries all data for user 20221192@nileuniversity.edu.ng
"""
from app import create_app, db
from sqlalchemy import text
import json

app = create_app()
with app.app_context():
    from app.models.user import User
    from app.models.course import Course
    from app.models.session import ScheduleBlock, StudySession
    from app.models.adaptation_log import AdaptationLog
    from app.models.timetable_entry import TimetableEntry

    user = User.query.filter_by(email='20221192@nileuniversity.edu.ng').first()
    if not user:
        print("USER NOT FOUND")
        exit()

    uid = user.id

    # ══════════════════════════════════════════════════════
    # TASK 1 — USER PROFILE
    # ══════════════════════════════════════════════════════
    print("=" * 60)
    print("TASK 1 — USER PROFILE")
    print("=" * 60)
    print(f"  username:               {user.username}")
    print(f"  email:                  {user.email}")
    print(f"  level:                  {user.level}")
    print(f"  base_template:          {getattr(user, 'base_template', 'N/A')}")
    print(f"  peak_time:              {getattr(user, 'peak_time', 'N/A')}")
    print(f"  focus_threshold:        {getattr(user, 'focus_threshold', 'N/A')}")
    print(f"  learning_style:         {getattr(user, 'learning_style', 'N/A')}")
    print(f"  daily_cognitive_budget:  {getattr(user, 'daily_cognitive_budget', 'N/A')}")
    print(f"  vark_visual:            {getattr(user, 'vark_visual', 'N/A')}")
    print(f"  vark_aural:             {getattr(user, 'vark_aural', 'N/A')}")
    print(f"  vark_read_write:        {getattr(user, 'vark_read_write', 'N/A')}")
    print(f"  vark_kinesthetic:       {getattr(user, 'vark_kinesthetic', 'N/A')}")
    print(f"  xp_points:              {user.xp_points}")
    print(f"  streak_count:           {user.streak_count}")
    print(f"  badge:                  {user.badge}")
    print(f"  is_verified:            {getattr(user, 'is_verified', 'N/A')}")

    # Enrolled courses
    print(f"\n  ENROLLED COURSES:")
    if hasattr(user, 'courses'):
        for c in user.courses:
            print(f"    - {c.code}: {c.name} (weight={getattr(c, 'weight', 'N/A')}, credits={c.credits})")
    else:
        # Try via user_courses join table
        result = db.session.execute(text(
            "SELECT c.code, c.name, c.weight, c.credits "
            "FROM course c JOIN user_courses uc ON c.id = uc.course_id "
            "WHERE uc.user_id = :uid"
        ), {'uid': uid})
        rows = result.fetchall()
        if rows:
            for r in rows:
                print(f"    - {r[0]}: {r[1]} (weight={r[2]}, credits={r[3]})")
        else:
            print("    (no courses enrolled)")

    # ══════════════════════════════════════════════════════
    # TASK 3 — GENERATED SCHEDULE (current week blocks)
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TASK 3 — GENERATED SCHEDULE BLOCKS")
    print("=" * 60)
    blocks = ScheduleBlock.query.filter_by(user_id=uid).order_by(
        ScheduleBlock.day_of_week, ScheduleBlock.start_time
    ).all()
    if blocks:
        print(f"  {'Day':<12} {'Start':<10} {'End':<10} {'Course':<12} {'Technique'}")
        print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*12} {'-'*30}")
        for b in blocks:
            code = b.course.code if b.course else 'N/A'
            print(f"  {b.day_of_week:<12} {str(b.start_time):<10} {str(b.end_time):<10} {code:<12} {b.technique_name or 'N/A'}")
    else:
        print("  (no schedule blocks found)")

    # ══════════════════════════════════════════════════════
    # TASK 4 — ADAPTATION LOG
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TASK 4 — MOST RECENT ADAPTATION LOG")
    print("=" * 60)
    log = AdaptationLog.query.filter_by(user_id=uid).order_by(
        AdaptationLog.created_at.desc()
    ).first()
    if log:
        print(f"  week_label:  {log.week_label}")
        print(f"  summary:     {log.summary}")
        print(f"  created_at:  {log.created_at}")
        print(f"\n  FULL REASONING:")
        try:
            reasoning = json.loads(log.reasoning)
            print(json.dumps(reasoning, indent=4))
        except:
            print(f"  {log.reasoning}")
    else:
        print("  (no adaptation logs found)")

    # ══════════════════════════════════════════════════════
    # TASK 5 — SESSION DATA
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TASK 5 — STUDY SESSIONS")
    print("=" * 60)
    sessions = StudySession.query.filter_by(user_id=uid).order_by(
        StudySession.start_time.desc()
    ).all()
    if sessions:
        print(f"  {'Course':<12} {'Score':<8} {'Mood':<8} {'Duration':<10} {'Start Time'}")
        print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*20}")
        for s in sessions:
            code = s.course.code if s.course else 'N/A'
            dur = s.duration_minutes if s.duration_minutes else 'N/A'
            score = s.success_score if s.success_score is not None else 'N/A'
            mood = s.mood_after if s.mood_after is not None else 'N/A'
            print(f"  {code:<12} {str(score):<8} {str(mood):<8} {str(dur)+'m':<10} {s.start_time}")
    else:
        print("  (no study sessions found)")

    # ══════════════════════════════════════════════════════
    # TASK 6 — TIMETABLE ENTRIES
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TASK 6 — TIMETABLE ENTRIES")
    print("=" * 60)
    # TimetableEntry may or may not have a direct course relationship
    try:
        entries = TimetableEntry.query.filter_by(user_id=uid).order_by(
            TimetableEntry.day_of_week, TimetableEntry.start_time
        ).all()
        if entries:
            print(f"  {'Day':<12} {'Start':<10} {'End':<10} {'Course'}")
            print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*20}")
            for e in entries:
                course_info = ''
                if hasattr(e, 'course') and e.course:
                    course_info = e.course.code
                elif hasattr(e, 'course_code'):
                    course_info = e.course_code
                elif hasattr(e, 'course_name'):
                    course_info = e.course_name
                else:
                    course_info = getattr(e, 'title', 'N/A')
                print(f"  {e.day_of_week:<12} {str(e.start_time):<10} {str(e.end_time):<10} {course_info}")
        else:
            print("  (no timetable entries found)")
    except Exception as ex:
        print(f"  Error querying timetable: {ex}")

    print("\n" + "=" * 60)
    print("DATA RETRIEVAL COMPLETE")
    print("=" * 60)
