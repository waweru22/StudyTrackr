"""
Utility for running functions in background threads.
Used by NotificationService for non-blocking FCM push delivery.
"""
import threading


def create_task(func, *args, **kwargs):
    """Execute func(*args, **kwargs) in a daemon background thread.
    Returns the thread object for testing/debugging.
    Exceptions inside the thread are logged but never propagate."""
    def _wrapper():
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"[BACKGROUND_TASK] Error in {func.__name__}: {e}")

    thread = threading.Thread(target=_wrapper, daemon=True)
    thread.start()
    return thread
