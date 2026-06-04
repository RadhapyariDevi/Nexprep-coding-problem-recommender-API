def calibrate_difficulty(solved_stats: dict, contest_rating: float = None) -> dict:
    """
    Determines the user's recommended LeetCode difficulty level based on
    their solved problem distribution and optional contest rating.

    The function estimates the user's current skill level by analyzing
    their progression from Easy to Medium to Hard problems. If a contest
    rating is available, it is used as the primary indicator of ability.

    Returns the recommended difficulty, confidence score, and solve ratios
    used in the decision.
    """


    easy = solved_stats.get("easySolved", 0)
    medium = solved_stats.get("mediumSolved", 0)
    hard = solved_stats.get("hardSolved", 0)
    total = easy + medium + hard or 1

    medium_ratio = medium / max(easy, 1)
    hard_ratio = hard / max(medium, 1)

    # Determine user's zone
    if easy < 20:
        zone = "EASY"
        confidence = 0.9
    elif medium_ratio < 0.25:
        # They solved lots of Easy but barely touched Medium so
        zone = "MEDIUM"
        confidence = 0.85
    elif hard_ratio < 0.15:
        zone = "MEDIUM"  # still medium, but harder ones
        confidence = 0.7
    elif hard_ratio >= 0.15:
        zone = "HARD"
        confidence = 0.8
    else:
        zone = "MEDIUM"
        confidence = 0.6

    # contest rating is ground truth if available
    if contest_rating:
        if contest_rating < 1400:
            zone = "EASY"
        elif contest_rating < 1700:
            zone = "MEDIUM"
        elif contest_rating < 2000:
            zone = "MEDIUM"  # harder mediums
        else:
            zone = "HARD"
        confidence = 0.95  
    
    return {
        "recommended_difficulty": zone,
        "confidence": confidence,
        "medium_to_easy_ratio": round(medium_ratio, 2),
        "hard_to_medium_ratio": round(hard_ratio, 2)
    }

