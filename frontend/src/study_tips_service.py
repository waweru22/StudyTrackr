import random

class StudyTipsService:
    TIPS = [
        {
            "id": 1,
            "title": "Pomodoro Technique",
            "rating": 3,
            "summary": "A time management method that breaks work into focused intervals (typically 25 minutes) separated by short breaks, creating structured productivity cycles that maintain concentration while preventing mental fatigue and burnout.",
            "description": "Explain a concept in simple terms as if teaching a beginner.",
            "use_case": "Procrastination, long study sessions, staying disciplined.",
            "se_tip": "Treat study sessions like sprint cycles: focused work followed by a short deploy break.",
            "combinations": ["Active Recall", "Spaced Repetition", "Feynman Technique"],
            "how_to_use": [
                "Pick one clear task (not 'study DBMS' → 'revise normalization').",
                "Set a timer for 25 minutes and work with zero distractions.",
                "Take a 5-minute break after each session.",
                "After 4 cycles, take a longer break of 15–30 minutes.",
            ],
            "why_it_works": [
                "Uses time pressure to force focus.",
                "Prevents mental fatigue by breaking work into manageable chunks.",
                "Builds a consistent rhythm without letting tasks feel endless.",
            ],
            "best_for": ["Procrastination", "Long study sessions", "Staying disciplined"],
            "common_mistakes": [
                "Studying passively without an active goal.",
                "Using breaks for social media or distractions.",
                "Choosing tasks that are too vague.",
            ],
            "example": "Use 25/5 for beginners, 50/10 for deeper work, and track Pomodoros per subject.",
        },
        {
            "id": 2,
            "title": "Active Recall",
            "rating": 3,
            "summary": "An evidence-based learning technique that actively stimulates memory retrieval by testing yourself on information rather than passively reviewing notes, strengthening neural pathways and improving long-term retention.",
            "description": "Close your notes and ask yourself specific questions. Say or write answers from memory, then check them.",
            "use_case": "Exams, memorization-heavy courses, definitions and concepts.",
            "se_tip": "Use flashcards and practice questions like debugging your memory with tests.",
            "combinations": ["Pomodoro Technique", "Spaced Repetition", "Blurting Method"],
            "how_to_use": [
                "Close your notes and ask yourself specific questions.",
                "Say or write answers from memory.",
                "Check and correct yourself immediately.",
            ],
            "why_it_works": [
                "Strengthens retrieval pathways like training a muscle.",
                "Exams test recall, not recognition.",
                "Makes learning active instead of passive.",
            ],
            "best_for": ["Exams", "Memorization-heavy courses", "Definitions and concepts"],
            "common_mistakes": [
                "Looking at notes too quickly.",
                "Mistaking familiarity for understanding.",
                "Only rereading without retrieval practice.",
            ],
            "example": "Use flashcards, practice questions, or teach the concept out loud.",
        },
        {
            "id": 3,
            "title": "Spaced Repetition",
            "rating": 2,
            "summary": "A learning technique that leverages the psychological spacing effect by reviewing material at gradually increasing intervals, optimizing memory consolidation and combating the natural forgetting curve for superior long-term knowledge retention.",
            "description": "Schedule reviews at spaced intervals to fight the forgetting curve.",
            "use_case": "Long-term retention, learning languages, large content volumes.",
            "se_tip": "Review old PRs or design notes on a schedule instead of only tackling fresh work.",
            "combinations": ["Active Recall", "Pomodoro Technique", "Chunking"],
            "how_to_use": [
                "Review content on Day 1, Day 2, Day 4, Day 7, Day 14.",
                "Use spaced repetition tools like Anki or Quizlet.",
                "Add new cards gradually and keep review sessions focused.",
            ],
            "why_it_works": [
                "Targets the forgetting curve.",
                "Reviews happen right before you forget.",
                "Transforms short-term learning into durable retention.",
            ],
            "best_for": ["Long-term retention", "Learning languages", "Large content volumes"],
            "common_mistakes": [
                "Cramming instead of spacing.",
                "Reviewing too often and wasting time.",
                "Skipping the planned intervals.",
            ],
            "example": "Anki is best; Quizlet is simpler for quick review.",
        },
        {
            "id": 4,
            "title": "Feynman Technique",
            "rating": 2,
            "summary": "A powerful learning method named after physicist Richard Feynman that involves explaining complex concepts in simple terms to identify knowledge gaps, promoting deep understanding rather than surface-level memorization.",
            "description": "Take a concept, explain it simply, and then refine until it is clear.",
            "use_case": "Complex subjects, math, programming, and theory.",
            "se_tip": "Write a small tutorial or internal doc as if explaining a feature to a junior dev.",
            "combinations": ["Active Recall", "Chunking", "Interleaving"],
            "how_to_use": [
                "Study a topic fully.",
                "Explain it in simple terms as if teaching a 10-year-old.",
                "Identify gaps, relearn, and simplify again.",
            ],
            "why_it_works": [
                "Forces clarity instead of memorization.",
                "Exposes fake understanding instantly.",
                "Turns concepts into usable mental models.",
            ],
            "best_for": ["Complex subjects", "Math", "Programming", "Theory"],
            "common_mistakes": [
                "Using jargon instead of simplification.",
                "Memorizing definitions without understanding.",
                "Skipping the gap-finding step.",
            ],
            "example": "Record yourself explaining the topic or write a simple tutorial.",
        },
        {
            "id": 5,
            "title": "Blurting Method",
            "rating": 2,
            "summary": "A rapid assessment technique where you write down everything you can remember about a topic immediately after studying, then compare with your notes to identify knowledge gaps and reinforce learning through immediate feedback.",
            "description": "Study briefly, close your materials, write what you remember, then fill the gaps.",
            "use_case": "Quick revision, identifying weak areas.",
            "se_tip": "Use it like a bug reproduction checklist: capture what you know, then find what is missing.",
            "combinations": ["Active Recall", "Pomodoro Technique", "Spaced Repetition"],
            "how_to_use": [
                "Study a topic briefly.",
                "Close everything and write what you remember.",
                "Compare with notes and highlight missing points.",
            ],
            "why_it_works": [
                "Combines active recall with self-testing.",
                "Shows exactly what you still need to learn.",
                "Reveals weak areas quickly.",
            ],
            "best_for": ["Quick revision", "Identifying weak areas"],
            "common_mistakes": [
                "Writing while checking notes.",
                "Not correcting errors afterward.",
                "Skipping the comparison step.",
            ],
            "example": "Topic: OSI model → write layers, then fill gaps from notes.",
        },
        {
            "id": 6,
            "title": "Chunking",
            "rating": 2,
            "summary": "A cognitive strategy that organizes information into meaningful groups or patterns, reducing cognitive load and making complex information more manageable and memorable by leveraging the brain's preference for structured patterns over isolated facts.",
            "description": "Break big information into categories, patterns, or themes instead of memorizing isolated facts.",
            "use_case": "Overwhelming topics, structured subjects, large knowledge sets.",
            "se_tip": "Group related components or modules into logical subsystems before memorizing details.",
            "combinations": ["Feynman Technique", "Interleaving", "Spaced Repetition"],
            "how_to_use": [
                "Break big information into categories, patterns, or themes.",
                "Create meaningful groups instead of memorizing isolated facts.",
                "Review each chunk as a unit.",
            ],
            "why_it_works": [
                "Brain prefers patterns over randomness.",
                "Reduces cognitive load by organizing knowledge.",
                "Makes large subjects easier to recall.",
            ],
            "best_for": ["Overwhelming topics", "Structured subjects", "Large data sets"],
            "common_mistakes": [
                "Making chunks too large.",
                "Creating groups that don’t connect.",
                "Memorizing chunks without understanding their relationships.",
            ],
            "example": "Networking facts → group by layers, protocols, and devices.",
        },
        {
            "id": 7,
            "title": "Interleaving",
            "rating": 3,
            "summary": "An advanced learning strategy that mixes different topics or problem types within a single study session, improving pattern recognition, problem-solving skills, and the ability to discriminate between similar concepts.",
            "description": "Alternate between related subjects to improve adaptability and pattern recognition.",
            "use_case": "Math, coding, problem-solving subjects.",
            "se_tip": "Switch between algorithms, systems design, and debugging practice instead of staying on one topic all day.",
            "combinations": ["Chunking", "Feynman Technique", "Active Recall"],
            "how_to_use": [
                "Switch topics every 20–40 minutes.",
                "Mix different problem types within a session.",
                "Use interleaving after you already understand the basics.",
            ],
            "why_it_works": [
                "Improves adaptability and problem-solving.",
                "Helps the brain recognize patterns across topics.",
                "Prevents mental stagnation from one-topic repetition.",
            ],
            "best_for": ["Math", "Coding", "Problem-solving subjects"],
            "common_mistakes": [
                "Switching too fast and losing depth.",
                "Using interleaving before basic mastery.",
                "Treating topics as unrelated rather than connected.",
            ],
            "example": "Study SQL, networking, and algorithms in the same block instead of only one subject.",
        },
        {
            "id": 8,
            "title": "SQ3R Method",
            "rating": 1,
            "summary": "A structured reading comprehension technique (Survey, Question, Read, Recite, Review) that transforms passive reading into an active learning process, though less effective than modern evidence-based methods for most learners.",
            "description": "Survey, Question, Read, Recite, Review to make reading intentional and memorable.",
            "use_case": "Textbooks, theory-heavy courses.",
            "se_tip": "Survey docs or spec sections first, then read with questions in mind like code review goals.",
            "combinations": ["Active Recall", "Chunking"],
            "how_to_use": [
                "Survey: skim headings and structure.",
                "Question: ask what each section will teach.",
                "Read actively with a focus on answers.",
                "Recite: summarize from memory.",
                "Review key points afterward.",
            ],
            "why_it_works": [
                "Makes reading active instead of passive.",
                "Prepares your brain for retention before deep study.",
                "Helps you remember textbook material more efficiently.",
            ],
            "best_for": ["Textbooks", "Theory-heavy courses"],
            "common_mistakes": [
                "Highlighting everything.",
                "Reading without questioning.",
                "Skipping the review step.",
            ],
            "example": "Use SQ3R on one textbook chapter, then apply active recall afterward.",
        },
    ]

    @staticmethod
    def get_tips():
        return StudyTipsService.TIPS

    @staticmethod
    def get_featured_tip():
        tip = random.choice(StudyTipsService.TIPS)
        tip_copy = tip.copy()
        tip_copy['type'] = 'tip'
        tip_copy['timestamp'] = "Featured"
        return tip_copy
