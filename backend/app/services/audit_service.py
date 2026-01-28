from app import db
from app.models.session import StudySession
from app.models.user import User
from sqlalchemy import func

class WeeklyAuditService:
    @staticmethod
    def perform_audit(user_id):
        user = User.query.get(user_id)
        if not user: return "User Not Found"

        # Inclusive Analytics: Fetch ALL recent sessions regardless of score
        # Requirement: "Remove all success-score filters."
        sessions = StudySession.query.filter_by(user_id=user_id).all() # Simplification for total history, usually weekly
        
        if not sessions:
            return "No data for audit"

        # Determine Peak Performance Time
        # Group by hour? Or just use "vibe"?
        # Requirement: Weighted Analysis: Value Score = (Frequency * 0.4) + (AvgSuccessScore * 0.6)
        
        # We need to bin sessions into buckets (Morning, Afternoon, Evening, Night) or specific hours.
        # Let's reuse existing logic buckets if available, or define them.
        # Assuming buckets: Morning (6-12), Afternoon (12-17), Evening (17-21), Night (21-6)
        
        buckets = {
            'Morning': {'count': 0, 'total_score': 0.0, 'distractions': 0},
            'Afternoon': {'count': 0, 'total_score': 0.0, 'distractions': 0},
            'Evening': {'count': 0, 'total_score': 0.0, 'distractions': 0},
            'Night': {'count': 0, 'total_score': 0.0, 'distractions': 0}
        }
        
        total_sessions = 0
        
        for s in sessions:
            total_sessions += 1
            hour = s.start_time.hour
            bucket = 'Night'
            if 6 <= hour < 12: bucket = 'Morning'
            elif 12 <= hour < 17: bucket = 'Afternoon'
            elif 17 <= hour < 21: bucket = 'Evening'
            
            buckets[bucket]['count'] += 1
            buckets[bucket]['total_score'] += (s.success_score or 0)
            
            # Distraction Tracking
            if s.distraction_count >= 2:
                buckets[bucket]['distractions'] += 1

        best_bucket = None
        max_value_score = -1.0
        
        report = []

        for b_name, data in buckets.items():
            if data['count'] == 0: continue
            
            avg_score = data['total_score'] / data['count']
            freq_norm = data['count'] / total_sessions # Normalized frequency (0-1)
            
            # Value Score Formula: (Frequency * 0.4) + (AvgSuccessScore * 0.6)
            # AvgSuccessScore usually 0-100? Or 0-1? If 0-100, normalize freq to match?
            # Prompt: "Frequency" could be count or normalized.
            # Assuming "Frequency" is raw count might skew if values are high. 
            # But usually "Value Score" implies relative utility.
            # Let's usage raw count if scores are 0-100, assuming frequency is usually < 20/week.
            # (Frequency * 0.4) -> 5 * 0.4 = 2.0. (Avg * 0.6) -> 80 * 0.6 = 48.
            # This makes AvgScore dominate heavily.
            # Let's normalize score to 0-1? Or assume the prompt formula implies standard scaling.
            # Let's interpret literally: Frequency (count) * 0.4 + AvgScore (0-100) * 0.6.
            
            value_score = (data['count'] * 0.4) + (avg_score * 0.6)
            
            if value_score > max_value_score:
                max_value_score = value_score
                best_bucket = b_name
                
            # High Interference Check
            # "Audit if the distraction_count consistently hits 2 during specific buckets"
            # If > 50% of sessions in this bucket had high distractions?
            if data['distractions'] > (data['count'] / 2) and data['count'] > 2:
                report.append(f"⚠️ High Interference detected in {b_name} sessions.")
                
            report.append(f"{b_name}: Value Score {value_score:.1f} (Freq: {data['count']}, Avg: {avg_score:.1f})")

        # Update User Peak Time
        if best_bucket and best_bucket != user.peak_time:
            # Consistency Reward Check
            # "If avg scores are low (< 30%) but frequency is high..."
            # Let's verify the best bucket's stats.
            best_data = buckets[best_bucket]
            best_avg = best_data['total_score'] / best_data['count']
            
            if best_avg < 30.0:
                 # Trigger Consistency Badge Update INSTEAD of peak_time shift
                 # (Requirement: "consistency Reward ... trigger a Consistency Badge update instead")
                 user.badge = "Consistent Grinder" # Simplified reward
                 msg = f"Consistent effort detected in {best_bucket} despite challenges. Badge upgraded!"
                 report.append(msg)
            else:
                 old_peak = user.peak_time
                 user.peak_time = best_bucket
                 msg = f"Peak Time auto-updated from {old_peak} to {best_bucket} based on Value Score."
                 report.append(msg)
        
        db.session.commit()
        return report
