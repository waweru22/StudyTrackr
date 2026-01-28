from app import create_app, db
from app.services.rule_engine import RuleEngine
from app.models.course import StudyKnowledge, Course
from app.models.session import StudySession, ScheduleBlock

app = create_app()

with app.app_context():
    print("--- Verifying Rule Engine ---")
    
    # 1. Verify Knowledge Base Seeding
    print("Checking Rules in DB...")
    rules = StudyKnowledge.query.all()
    print(f"Found {len(rules)} rules.")
    interleaving_rule = StudyKnowledge.query.filter(StudyKnowledge.principle.contains("Interleaving")).first()
    assert interleaving_rule is not None
    print(f"Found Rule: {interleaving_rule.principle}")
    
    # 2. Verify Rule Parsing Logic
    print("\nTesting Rule Parser...")
    # Context that matches Interleaving (> 180 min)
    context_match = {'cumulative_course_minutes': 200, 'session_vibe': 'Normal'}
    active_rules = RuleEngine.evaluate_triggers(context_match)
    print(f"Context {context_match} -> Active Rules: {[r.principle for r in active_rules]}")
    assert any("Interleaving" in r.principle for r in active_rules)
    
    # Context that matches Zeigarnik (High Frustration)
    context_frust = {'session_vibe': 'High Frustration'}
    active_frust = RuleEngine.evaluate_triggers(context_frust)
    print(f"Context {context_frust} -> Active Rules: {[r.principle for r in active_frust]}")
    assert any("Zeigarnik" in r.principle for r in active_frust)
    
    print("\n✅ Rule Engine Logic Verified.")
