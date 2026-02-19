from app import create_app, db
from app.models.course import Course, StudyKnowledge
# StudyTemplate removed

app = create_app()

def seed_courses():
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
        {"code":"NUN-COS305", "name":"Remote Work and Collaboration", "weight":1, "level":300, "semester":1, "credits":2}
    ]

    for c_data in courses:
        if not Course.query.filter_by(code=c_data['code']).first():
            db.session.add(Course(**c_data))
            print(f"Added Course: {c_data['code']}")

    # 2. Seed Base Templates (Structural Logic for the Inference Engine)
    # Skipped due to missing StudyTemplate model

    # --- Seed Knowledge Base for Inference (Expert System Rules) ---
    tips = [
      {
        "principle": "Recall-Gated Consolidation",
        "rule_logic": "Exponential Signal-to-Noise Ratio (SNR) Improvement",
        "content": "Consistency in study environment acts as a filter for the long-term memory (LTM) system. Repeatedly studying the same course in a fixed location allows the brain to 'shield' memories from extraneous noise.",
        "inference_trigger": "If session_location_consistency > 0.8 AND course_weight >= 4, increase session_efficacy_multiplier by 1.5x.",
        "academic_source": "eLife (Recall-Gated Consolidation Theory, 2024)",
        "tags": "Environment, Exponential Growth, Consolidation"
      },
      {
        "principle": "Desirable Difficulties (Interleaving)",
        "rule_logic": "Blocked-to-Interleaved Transition",
        "content": "For complex logic, initial learning should be 'blocked'. Once basic competency is reached, switch to 'Interleaved' scheduling.",
        "inference_trigger": "If cumulative_course_minutes > 180, modify schedule from 'Blocked' to 'Interleaved' for next 3 sessions.",
        "academic_source": "Bjork & Bjork (2011)",
        "tags": "Interleaving, Logic Transfer"
      },
      {
        "principle": "The Zeigarnik tactical Break",
        "rule_logic": "Interrupted Task Recall Enhancement",
        "content": "Incomplete tasks create higher mental tension and better recall. A 5-minute distraction log utilizes 'attention residue'.",
        "inference_trigger": "If session_vibe == 'High Frustration', trigger mandatory 'Distraction Log' (5-min) to activate Diffuse Mode.",
        "academic_source": "Dr. Barbara Oakley",
        "tags": "Breaks, Problem Solving"
      },
      {
        "principle": "The 2-3-5-7 Spaced Interval",
        "rule_logic": "Forgetting Curve Reset Algorithm",
        "content": "To counteract memory decay, info must be retrieved at strategic intervals.",
        "inference_trigger": "On Session_End(Success), auto-generate 'Review_Blocks' in schedule at T+1d, T+3d, and T+7d.",
        "academic_source": "Ebbinghaus / Cornell LSC",
        "tags": "Spaced Repetition, Algorithm"
      },
      {
        "principle": "The Focus Threshold Cap",
        "rule_logic": "Fatigue-Induced Error Prevention",
        "content": "Cognitive performance drops after the focus threshold. Forcing study beyond this leads to 'pseudostudying'.",
        "inference_trigger": "If current_session_duration > user_focus_threshold, trigger 'Mandatory Rest' state.",
        "academic_source": "Expert Systems with Applications (2023)",
        "tags": "Focus, Threshold"
      },
      {
        "principle": "Behavioral Anchor Alignment",
        "rule_logic": "Circadian Rhythm Correction",
        "content": "Objective behavioral logs are prioritized over subjective onboarding data to ensure biological alignment.",
        "inference_trigger": "If weekly_audit_success_rate(actual_peak) > weekly_audit_success_rate(onboard_peak) by 20%, update student_profile.peak_time.",
        "academic_source": "Journal of Biological Rhythms (2022)",
        "tags": "Audit, Optimization"
      },
      {
        "principle": "The Feynman Technique",
        "rule_logic": "Deep Processing & Simplification",
        "content": "To learn deep concepts, teaching it in simple terms exposes gaps in understanding. High complexity requires active reconstruction.",
        "inference_trigger": "If course_weight >= 4, suggest 'The Feynman Technique'.",
        "academic_source": "eLife (2024)",
        "tags": "Deep Work, Simplification"
      },
      {
        "principle": "Pomodoro Technique",
        "rule_logic": "Time-Boxing for Focus",
        "content": "25 minutes intense focus, 5 minutes break. Used to combat procrastination and maintain stamina on lower cognitive load tasks.",
        "inference_trigger": "If course_weight <= 2, suggest 'Pomodoro' to maintain momentum.",
        "academic_source": "Cirillo (1980)",
        "tags": "Time Management, Focus"
      },
      {
        "principle": "Blurting (Active Recall)",
        "rule_logic": "Retrieval Practice",
        "content": "Write down everything you know about a topic from memory, then check against notes. Best for factual subjects.",
        "inference_trigger": "If course_weight == 3, suggest 'Blurting'.",
        "academic_source": "Roediger & Karpicke (2006)",
        "tags": "Active Recall, Memory"
      },
      {
        "principle": "Cognitive Load Balancing",
        "rule_logic": "Resource Depletion Management",
        "content": "Deep Work depletes cognitive resources faster. Budget constraints prevent burnout.",
        "inference_trigger": "If daily_cognitive_load > daily_cognitive_budget, reschedule overflow to next day.",
        "academic_source": "Sweller (1988)",
        "tags": "Cognitive Load, Budget"
      }, 
      {
        "principle": "Circadian Energy Mapping",
        "rule_logic": "Vibe-to-Complexity Alignment",
        "content": "High-complexity tasks (Weight 5) should only be scheduled during 'High Energy' vibes. Low energy states require 'Administrative' or 'Review' tasks to prevent burnout.",
        "inference_trigger": "If session_vibe == 'Low Energy' AND course_weight >= 4, swap technique to 'Pomodoro' and limit duration to 25 mins.",
        "academic_source": "Biological Rhythm Research (2023)",
        "tags": "Vibe, Energy, Complexity"
      },
      {
        "principle": "Environmental Contextualization",
        "rule_logic": "Location-Based Cognitive Load",
        "content": "Public environments like 'Cafe' or 'Class' increase auditory distractions. Solo/Deep Work techniques are less effective here than group-based or active recall methods.",
        "inference_trigger": "If session_environment in ['Class', 'Other'] AND social_setting == 'Group', prioritize 'Feynman Technique' (Peer Teaching mode).",
        "academic_source": "Environmental Psychology Review",
        "tags": "Environment, Social, Context"
      },
      {
        "principle": "Template Enforcement (Deep Work)",
        "rule_logic": "Contiguous Block Allocation",
        "content": "The Deep Work template requires 90-120 minute uninterrupted blocks. The system must merge standard 60-min blocks for high-weight courses.",
        "inference_trigger": "If base_template == 'deep_work' AND course_weight >= 4, merge adjacent schedule slots into a single 120-min block.",
        "academic_source": "Cal Newport (Deep Work)",
        "tags": "Deep Work, Template"
      }
    ]
    
    for t_data in tips:
        # Check by principle to avoid dupes
        if not StudyKnowledge.query.filter_by(principle=t_data['principle']).first():
            db.session.add(StudyKnowledge(**t_data))
            print(f"Added Knowledge: {t_data['principle']}")

    db.session.commit()
    print("Seeding Complete: Curriculum & Expert System Rules loaded.")

if __name__ == '__main__':
    with app.app_context():
        seed_courses()
