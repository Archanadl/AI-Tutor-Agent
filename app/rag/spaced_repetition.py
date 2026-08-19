def calculate_sm2(
    quality: int, 
    interval: int = 0, 
    repetitions: int = 0, 
    ease_factor: float = 2.5
) -> tuple[int, int, float]:
    """
    Calculates the next review interval using the SuperMemo-2 (SM-2) algorithm.
    
    Quality scale:
    0-2: Incorrect responses
    3-5: Correct responses (3 = hard, 4 = good, 5 = easy)
    """
    if quality >= 3:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1
    else:
        repetitions = 0
        interval = 1

    # Update ease factor
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # Ease factor cannot drop below 1.3
    if ease_factor < 1.3:
        ease_factor = 1.3

    return interval, repetitions, ease_factor