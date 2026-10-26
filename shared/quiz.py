"""Keep track of the quiz streak."""


def update_streak(streak: int, best: int, correct: bool) -> tuple[int, int]:
    """Return the new (streak, best streak) after a correct answer or a skip."""
    streak = streak + 1 if correct else 0
    return streak, max(best, streak)
