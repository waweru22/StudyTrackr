"""
Migration: Real-time Notification System (Phases 1 + 2.5)
- Creates notification_trigger table + seeds 10 default triggers
- Adds trigger_id, action_url, dismissed_at, push_sent, push_sent_at to notification
- Creates fcm_token table
- Marks existing notifications push_sent=True (legacy, can't send retroactively)
Safe to run multiple times.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

SEED_TRIGGERS = [
    # (trigger_name, description, is_active, priority, notification_type, send_push, template_title, template_message)
    (
        'badge_earned',
        'User earned a new badge by crossing an XP threshold',
        True, 'medium', 'achievement', True,
        'Badge Earned! {badge_name}',
        "You've reached {xp} XP and unlocked the {badge_name} badge. Great work!"
    ),
    (
        'burnout_warning',
        'Detected 2+ low energy sessions in the last 3 sessions',
        True, 'urgent', 'warning', True,
        'Burnout Detected',
        "We noticed you've had low energy in recent sessions. Let's reduce your workload and take a break."
    ),
    (
        'streak_milestone',
        'Streak reached 7, 14, 30, or 60 days',
        True, 'low', 'achievement', True,
        '{streak}-Day Streak!',
        "Amazing consistency! You've completed sessions for {streak} consecutive days."
    ),
    (
        'low_efficacy_session',
        'Session completed with success_score < 2',
        True, 'low', 'tip', True,
        "Session Didn't Go Well",
        "That {course_name} session didn't feel productive (scored {score}/5). Try a different technique next time."
    ),
    (
        'missed_session',
        'Scheduled block was not completed on time',
        True, 'medium', 'warning', True,
        'You Missed a Session',
        "You missed {course_name} at {time}. No worries - let's get back on track."
    ),
    # Phase 3 placeholders (inactive)
    (
        'course_struggling',
        'Student consistently performing poorly in a course',
        False, 'low', 'tip', False,
        'Struggling with {course_name}?',
        "Your recent {course_name} sessions show low scores. Consider reviewing materials or trying a different study technique."
    ),
    (
        'peak_time_reminder',
        'Reminder to study during identified peak productivity hours',
        False, 'low', 'tip', False,
        'Peak Study Time',
        "Your most productive study time is {peak_time}. Consider scheduling a session now."
    ),
    (
        'weekly_insights',
        'Weekly summary of study performance and progress',
        False, 'low', 'insight', False,
        'Your Weekly Study Insights',
        "This week: {sessions_completed} sessions, {total_minutes} minutes studied, {avg_score} avg score."
    ),
    (
        'schedule_adapted',
        'Schedule was automatically adjusted by the inference engine',
        False, 'medium', 'insight', False,
        'Schedule Updated',
        "Your study schedule has been adapted based on recent performance. Check your new blocks."
    ),
    (
        'long_gap_alert',
        'Student has not studied for an extended period',
        False, 'low', 'tip', False,
        "It's Been a While",
        "You haven't had a study session in {days} days. A short session can help you get back on track."
    ),
]


def migrate():
    with app.app_context():
        engine = db.engine

        with engine.connect() as conn:
            # 1. Add new columns to notification table
            new_cols = [
                ("trigger_id", "INTEGER REFERENCES notification_trigger(id)"),
                ("action_url", "VARCHAR(200)"),
                ("dismissed_at", "DATETIME"),
                ("push_sent", "BOOLEAN DEFAULT 0"),
                ("push_sent_at", "DATETIME"),
            ]
            for col_name, col_def in new_cols:
                try:
                    conn.execute(text(f"ALTER TABLE notification ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                    print(f"[OK] Added '{col_name}' to notification.")
                except Exception as e:
                    print(f"[SKIP] notification.{col_name}: {e}")

            # 2. Mark existing notifications as push_sent=True (legacy)
            try:
                conn.execute(text("UPDATE notification SET push_sent = 1 WHERE push_sent IS NULL OR push_sent = 0"))
                conn.commit()
                print("[OK] Marked existing notifications push_sent=True.")
            except Exception as e:
                print(f"[SKIP] update push_sent: {e}")

        # 3. Create notification_trigger and fcm_token tables via models
        db.create_all()
        print("[OK] Ensured notification_trigger and fcm_token tables exist.")

        # 4. Seed default triggers
        from app.models.notification_trigger import NotificationTrigger
        seeded = 0
        for row in SEED_TRIGGERS:
            name = row[0]
            existing = NotificationTrigger.query.filter_by(trigger_name=name).first()
            if not existing:
                trigger = NotificationTrigger(
                    trigger_name=row[0],
                    description=row[1],
                    is_active=row[2],
                    priority=row[3],
                    notification_type=row[4],
                    send_push=row[5],
                    template_title=row[6],
                    template_message=row[7],
                )
                db.session.add(trigger)
                seeded += 1

        if seeded > 0:
            db.session.commit()
            print(f"[OK] Seeded {seeded} notification triggers.")
        else:
            print("[SKIP] All triggers already exist.")

    print("\nMigration complete.")


if __name__ == "__main__":
    migrate()
