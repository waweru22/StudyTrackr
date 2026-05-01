from app import db
from app.models.notification import Notification
from app.models.session import StudySession, ScheduleBlock
from app.models.user import User
from datetime import datetime, timedelta


class TriggerEvaluator:
    """
    Evaluates whether a notification trigger should fire for a given user/event.
    Each check method returns (should_fire: bool, context_data: dict | None).
    All methods include idempotency checks to prevent duplicate notifications.
    """

    # ── Badge Earned ──────────────────────────────────────────────────

    @staticmethod
    def check_badge_earned(user_id):
        """Check if user crossed an XP badge threshold.
        Thresholds: 1000 (Apprentice), 5000 (Master), 10000 (Grandmaster), 15000 (Legend)."""
        user = User.query.get(user_id)
        if not user:
            return False, None

        thresholds = [
            (15000, 'Legend'),
            (10000, 'Grandmaster'),
            (5000, 'Master'),
            (1000, 'Apprentice'),
        ]

        for xp_threshold, badge_name in thresholds:
            if user.xp_points >= xp_threshold:
                # Check if already notified for this badge in the last 30 days
                cutoff = datetime.utcnow() - timedelta(days=30)
                existing = Notification.query.join(
                    Notification.trigger
                ).filter(
                    Notification.user_id == user_id,
                    Notification.created_at >= cutoff,
                    Notification.trigger.has(trigger_name='badge_earned'),
                    Notification.message.contains(badge_name)
                ).first()

                if not existing:
                    return True, {'badge_name': badge_name, 'xp': user.xp_points}

        return False, None

    # ── Burnout Warning ───────────────────────────────────────────────

    @staticmethod
    def check_burnout_warning(user_id):
        """Check if 2+ of the user's last 3 sessions had 'Low Energy' vibe."""
        sessions = StudySession.query.filter_by(user_id=user_id).filter(
            StudySession.end_time.isnot(None)
        ).order_by(StudySession.start_time.desc()).limit(3).all()

        if len(sessions) < 3:
            return False, None

        low_energy_count = sum(1 for s in sessions if s.vibe == 'Low Energy')

        if low_energy_count >= 2:
            # Check if burnout_warning was sent in the last 24 hours
            cutoff = datetime.utcnow() - timedelta(hours=24)
            existing = Notification.query.join(
                Notification.trigger
            ).filter(
                Notification.user_id == user_id,
                Notification.created_at >= cutoff,
                Notification.trigger.has(trigger_name='burnout_warning')
            ).first()

            if not existing:
                return True, {}

        return False, None

    # ── Streak Milestone ──────────────────────────────────────────────

    @staticmethod
    def check_streak_milestone(user_id):
        """Check if streak is exactly 7, 14, 30, or 60 days."""
        user = User.query.get(user_id)
        if not user:
            return False, None

        milestones = [7, 14, 30, 60]
        if user.streak_count not in milestones:
            return False, None

        # Check if already notified for this streak value in the last hour
        cutoff = datetime.utcnow() - timedelta(hours=1)
        existing = Notification.query.join(
            Notification.trigger
        ).filter(
            Notification.user_id == user_id,
            Notification.created_at >= cutoff,
            Notification.trigger.has(trigger_name='streak_milestone'),
            Notification.message.contains(str(user.streak_count))
        ).first()

        if not existing:
            return True, {'streak': user.streak_count}

        return False, None

    # ── Low Efficacy Session ──────────────────────────────────────────

    @staticmethod
    def check_low_efficacy_session(user_id, session_id):
        """Check if session completed with success_score < 2."""
        session = StudySession.query.get(session_id)
        if not session or session.user_id != user_id:
            return False, None

        score = int(session.success_score or 0)
        if score >= 2:
            return False, None

        # Check if already notified for this exact session
        existing = Notification.query.join(
            Notification.trigger
        ).filter(
            Notification.user_id == user_id,
            Notification.trigger.has(trigger_name='low_efficacy_session'),
            Notification.message.contains(str(session_id))
        ).first()

        if existing:
            return False, None

        course_name = session.course.name if session.course else 'Unknown'
        return True, {'course_name': course_name, 'score': score, 'session_id': session_id}

    # ── Missed Session ────────────────────────────────────────────────

    @staticmethod
    def check_missed_session(user_id, schedule_block_id):
        """Check if a scheduled block was missed."""
        block = ScheduleBlock.query.get(schedule_block_id)
        if not block or block.user_id != user_id:
            return False, None

        # Check if already notified for this block
        block_identifier = f"block_{schedule_block_id}"
        existing = Notification.query.join(
            Notification.trigger
        ).filter(
            Notification.user_id == user_id,
            Notification.trigger.has(trigger_name='missed_session'),
            Notification.message.contains(block_identifier)
        ).first()

        if existing:
            return False, None

        course_name = block.course.code if block.course else 'General Block'
        time_str = block.start_time.strftime('%H:%M') if block.start_time else 'Unknown'
        return True, {
            'course_name': course_name,
            'time': time_str,
            'block_id': schedule_block_id,
        }
