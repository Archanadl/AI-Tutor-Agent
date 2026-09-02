def calculate_sm2(
    quality: int,
    interval: int = 0,
    repetitions: int = 0,
    ease_factor: float = 2.5,
) -> tuple[int, int, float]:

    if not 0 <= quality <= 5:
        raise ValueError("Quality must be between 0 and 5.")

    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)

        repetitions += 1

    ease_factor = ease_factor + (
        0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )

    ease_factor = max(1.3, ease_factor)

    return interval, repetitions, ease_factor