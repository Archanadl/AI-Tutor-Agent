def validate_input(
    goal: str,
    current_level: str,
    topics: list[str],
    daily_hours: float,
    duration_days: int
):
    """
    Validate the information required to create
    a personalized study plan.
    """

    if not goal or not goal.strip():
        raise ValueError("Goal cannot be empty.")

    if not current_level or not current_level.strip():
        raise ValueError("Current level cannot be empty.")

    if not topics:
        raise ValueError("At least one topic is required.")

    # Remove empty topic names
    cleaned_topics = [topic.strip() for topic in topics if topic.strip()]

    if not cleaned_topics:
        raise ValueError("At least one valid topic is required.")

    if daily_hours <= 0:
        raise ValueError("Daily study hours must be greater than 0.")

    if duration_days <= 0:
        raise ValueError("Duration must be greater than 0 days.")

    return {
        "goal": goal.strip(),
        "current_level": current_level.strip(),
        "topics": cleaned_topics,
        "daily_hours": daily_hours,
        "duration_days": duration_days
    }