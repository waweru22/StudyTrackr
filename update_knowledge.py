from app import create_app, db
from app.models.course import StudyKnowledge

app = create_app()

def update_kb():
    print("--- Updating Knowledge Base ---")
    
    principle = "The Focus Threshold Cap"
    entry = StudyKnowledge.query.filter_by(principle=principle).first()
    
    if entry:
        print(f"Found existing entry: {entry.principle}")
        entry.inference_trigger = "Notify user of focus decay"
        entry.content = "Cognitive performance drops after the focus threshold. Alerts will trigger to maintain high-intensity focus."
        db.session.commit()
        print("✅ Entry Updated.")
    else:
        # If not found, create (Fallback)
        print("Entry not found, creating new.")
        new_entry = StudyKnowledge(
            principle=principle,
            rule_logic="block_duration > user.focus_threshold",
            content="Cognitive performance drops after the focus threshold. Alerts will trigger to maintain high-intensity focus.",
            inference_trigger="Notify user of focus decay",
            academic_source="Newport (2016)",
            tags="Breaks, Flow"
        )
        db.session.add(new_entry)
        db.session.commit()
        print("✅ Entry Created.")

if __name__ == '__main__':
    with app.app_context():
        update_kb()
