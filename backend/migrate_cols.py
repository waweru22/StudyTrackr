from app import create_app, db

app = create_app()

with app.app_context():
    conn = db.engine.connect()
    
    # StudyKnowledge new columns
    try:
        conn.execute(db.text("ALTER TABLE study_knowledge ADD COLUMN rule_type VARCHAR(20) DEFAULT 'schedule'"))
        print("Added study_knowledge.rule_type")
    except Exception as e:
        print(f"rule_type: {e}")
    
    try:
        conn.execute(db.text("ALTER TABLE study_knowledge ADD COLUMN student_instruction TEXT"))
        print("Added study_knowledge.student_instruction")
    except Exception as e:
        print(f"student_instruction: {e}")
    
    # ScheduleBlock new columns
    try:
        conn.execute(db.text("ALTER TABLE schedule_block ADD COLUMN suggested_environment VARCHAR(100)"))
        print("Added schedule_block.suggested_environment")
    except Exception as e:
        print(f"suggested_environment: {e}")
    
    try:
        conn.execute(db.text("ALTER TABLE schedule_block ADD COLUMN suggested_social_setting VARCHAR(50)"))
        print("Added schedule_block.suggested_social_setting")
    except Exception as e:
        print(f"suggested_social_setting: {e}")
    
    try:
        conn.execute(db.text("ALTER TABLE schedule_block ADD COLUMN suggested_medium VARCHAR(50)"))
        print("Added schedule_block.suggested_medium")
    except Exception as e:
        print(f"suggested_medium: {e}")
    
    conn.commit()
    conn.close()
    print("All ALTER TABLE done")
