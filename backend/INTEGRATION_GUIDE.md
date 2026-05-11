# Schedule Adaptation — Integration Guide

## Overview

The **AdaptationEngine** adds end-of-week schedule adaptation to
StudyTrackr. When a student hits "Regenerate" (or the system triggers
it on Sunday), the engine:

1. Analyses all completed sessions from the current week
2. Calculates per-course, per-technique effectiveness
3. Swaps underperforming techniques and shifts time-slots
4. Regenerates the schedule with adaptations applied
5. Populates `refinement_reason`, `academic_citation`, and
   `logic_explanation` on every adapted `ScheduleBlock`

---

## Files Changed

| Action   | File                                                 | Purpose                                        |
|----------|------------------------------------------------------|------------------------------------------------|
| **NEW**  | `app/services/inference_service_adaptation.py`       | `AdaptationEngine` class – all adaptation logic |
| **NEW**  | `test_adaptation_10day.py`                           | Standalone test suite                           |
| **MOD**  | `app/routes/schedule_routes.py`                      | `/regenerate` now calls AdaptationEngine        |
| **NEW**  | `INTEGRATION_GUIDE.md`                               | This file                                       |

---

## Step-by-Step Integration

### 1. Verify the new service file exists

```
backend/app/services/inference_service_adaptation.py
```

This file is self-contained. It imports from existing models and
services only — no new dependencies required.

### 2. Verify the route change

Open `backend/app/routes/schedule_routes.py` and confirm the
`/regenerate` endpoint now imports `AdaptationEngine`:

```python
@schedule_bp.route('/regenerate', methods=['POST'])
@jwt_required()
def regenerate_schedule():
    ...
    from app.services.inference_service_adaptation import AdaptationEngine
    result = AdaptationEngine.adapt_schedule_for_next_week(user_id)
    ...
```

### 3. Run the test suite

```bash
cd backend
python test_adaptation_10day.py
```

Expected output sections:
1. `=== WEEK 1 SCHEDULE ===` — all generated blocks
2. `=== SIMULATING 7 STUDY SESSIONS ===` — feedback data
3. `=== WEEKLY PERFORMANCE ANALYSIS ===` — per-course breakdown
4. `=== ADAPTATION DECISIONS ===` — what changed and why
5. `=== WEEK 2 SCHEDULE (ADAPTED) ===` — new blocks with reasons
6. `=== ADAPTATION SUMMARY ===` — change counts

Exit code `0` = success.

### 4. Test via the API

```bash
# With a valid JWT token:
curl -X POST http://localhost:5000/schedule/regenerate \
  -H "Authorization: Bearer <token>"
```

Response includes:
```json
{
  "message": "Schedule adapted (2 changes)",
  "adaptations_made": {
    "technique_swaps": 1,
    "time_shifts": 1,
    "total_courses": 3
  },
  "details": { ... }
}
```

---

## Decision Logic Summary

| Condition                                        | Action                    |
|--------------------------------------------------|---------------------------|
| `effectiveness < 2.0` AND `would_repeat < 0.5`  | **SWAP** technique        |
| `effectiveness ≥ 3.5` AND `would_repeat ≥ 0.7`  | **KEEP** technique        |
| `effectiveness < 2.5` AND `would_repeat < 0.6`  | **TRY** alternate         |
| Dominant mood = `Drained`                        | **SHIFT** time ±3 hours   |
| Dominant mood = `Energized`                      | **KEEP** time             |

---

## Known Edge Cases

| Scenario                          | Behaviour                                         |
|-----------------------------------|----------------------------------------------------|
| User has 0 completed sessions     | Falls back to standard `generate_week_schedule()`  |
| All sessions effectiveness ≥ 3.5  | Minimal/no changes — keeps working schedule        |
| All sessions effectiveness < 2.0  | Swaps all techniques to alternatives               |
| No sessions for a specific course | That course keeps its original schedule             |
| DB query fails                    | Caught by try/except; logs error, doesn't crash    |
| Time shift would go before 8 AM   | Clamped to 08:00                                   |
| Time shift would go after 22:00   | Clamped to 22:00                                   |

---

## Schema — No Migrations Needed

The adaptation uses only existing columns on `ScheduleBlock`:

- `refinement_reason` — `String(100)` — short label for the change
- `academic_citation` — `String(100)` — research reference
- `logic_explanation` — `String(255)` — detailed reasoning

And reads from existing `StudySession` columns:

- `success_score` → effectiveness
- `mood_after` → mood (1=Drained, 2=Neutral, 3=Energized)
- `would_repeat` → Boolean
- `learning_mode` → technique name

---

## How to Verify It's Working

1. **Run the test suite** — confirms the full pipeline end-to-end
2. **Check the Schedule page** — after regeneration, blocks should
   show `refinement_reason` values in the API response
3. **Check server logs** — look for `[Adaptation]` log lines:
   ```
   INFO:AdaptationEngine:[Adaptation] Analysed 7 sessions for user 12
   INFO:AdaptationEngine:[Adaptation] Schedule committed for user 12
   ```
