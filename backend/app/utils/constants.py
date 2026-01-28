# Technique Instructions & Timer Configurations

TECHNIQUE_INSTRUCTIONS = {
    "Deep Work": {
        "name": "Deep Work",  # <--- Added this to fix the KeyError
        "steps": [
            "Eliminate all distractions (phone away, notifications off).",
            "Define a single, clear goal for this 90-minute block.",
            "Maintain intense focus; log distractions only if necessary.",
            "End the session to commit progress to the Inference Engine."
        ],
        "timer_config": {"duration": 90, "intervals": []}
    },
    "Pomodoro": {
        "name": "Pomodoro", # <--- Added this to fix the KeyError
        "steps": [
            "Decide on the task to be done.",
            "Work with high intensity for the 25-minute sprint.",
            "Log interruptions using the 'Managed Distraction' button.",
            "Repeat for 4 cycles to reach maximum cognitive saturation."
        ],
        "timer_config": {"duration": 25, "intervals": [25, 5, 25, 5, 25, 5, 25, 30]}
    },
    "Active Recall": {
        "name": "Active Recall", # <--- Added this to fix the KeyError
        "steps": [
            "Review your material for a 5-minute priming window.",
            "Close all sources and perform a mental dump of the material.",
            "Check against the source and identify cognitive gaps.",
            "Repeat until retrieval becomes fluid."
        ],
        "timer_config": {"duration": 45, "intervals": [15, 5, 15, 5, 15]}
    }
}

PEAK_TIME_MAPPING = {
    "Morning": (6, 12),
    "Afternoon": (12, 17),
    "Evening": (17, 21),
    "Night": (21, 6) # Handles crossing midnight logic separately if needed
}
