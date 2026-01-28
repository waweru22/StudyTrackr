import random

class StudyTipsService:
    TIPS = [
        {
            "id": 1,
            "title": "Feynman Technique",
            "description": "Explain a concept in simple terms as if teaching a beginner.",
            "use_case": "Deep understanding of complex topics.",
            "se_tip": "Write documentation for your code before writing the code itself."
        },
        {
            "id": 2,
            "title": "Spaced Repetition",
            "description": "Review material at increasing intervals to exploit the spacing effect.",
            "use_case": "Long-term retention of syntax or algorithms.",
            "se_tip": "Review old PRs or architectural decisions months later to see if they hold up."
        },
        {
            "id": 3,
            "title": "Rubber Duck Debugging",
            "description": "Explain your code line-by-line to an inanimate object.",
            "use_case": "Debugging logic errors that you just can't see.",
            "se_tip": "Simply verbalizing the problem often reveals the solution immediately."
        },
        {
            "id": 4,
            "title": "SQ3R",
            "description": "Survey, Question, Read, Recite, Review.",
            "use_case": "Efficiently digesting technical documentation or textbooks.",
            "se_tip": "Survey API docs structure before diving into specific endpoints."
        },
        {
            "id": 5,
            "title": "Eat the Frog",
            "description": "Tackle your most difficult task first thing in the morning.",
            "use_case": "Overcoming procrastination on big features.",
            "se_tip": "Merge the most complex branch or fix the hardest bug before checking Slack."
        }
    ]

    @staticmethod
    def get_tips():
        return StudyTipsService.TIPS

    @staticmethod
    def get_featured_tip():
        tip = random.choice(StudyTipsService.TIPS)
        # Ensure it has a type for feed integration
        tip_copy = tip.copy()
        tip_copy['type'] = 'tip'
        tip_copy['timestamp'] = "Featured" # Placeholder for sorting if needed, though usually pinned
        return tip_copy
