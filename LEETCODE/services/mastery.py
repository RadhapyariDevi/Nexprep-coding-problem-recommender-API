import math
from collections import defaultdict
from typing import Dict, List

DIFFICULTY_WEIGHT = {
    "Easy":1.0,
    "Medium":2.5,
    "Hard":5.0
}

# Acceptance rate penalty

def acceptance_bonus(ac_rate: float) -> float:
    """Lower acceptance = harder = more credit. Normalized 0.8 to 2.0"""
    if ac_rate <= 0:
        return 1.0
    return max(0.8, 2.0-(ac_rate/100.0))


# recency weight : skills fade over time
def recency_weight(days_ago: int) -> float:
    """Exponential decay. Half-life ~90 days"""
    return math.exp(-0.693 * days_ago / 90)


# Main function

def build_mastery_vector(
    skill_stats: dict,
    ac_list: list,
    problem_details: dict,
    current_timestamp: int
)-> Dict[str, float]:
    
    raw_scores = defaultdict(float)

    level_weights = {
        "fundamental": 1.0,
        "intermediate": 2.0,
        "advanced": 3.5
    }

    for level, weight in level_weights.items():
        for item in skill_stats.get(level, []):
            tag = item.get("tagSlug", "")
            solved = item.get("problemsSolved", 0)
            if tag:
                raw_scores[tag] += solved * weight

    # Recency decay from submissions 
    for submission in ac_list:
        slug = submission.get("titleSlug", "")
        timestamp = submission.get("timestamp", current_timestamp)
        days_ago = (current_timestamp - int(timestamp)) / 86400
        problem = problem_details.get(slug, {})
        difficulty = problem.get("difficulty", "Medium")
        ac_rate = problem.get("acRate", 50.0)
        topics = problem.get("topicTags", [])

        # Main scoring formula
        score_contribution = (
            DIFFICULTY_WEIGHT.get(difficulty, 2.5)
            * acceptance_bonus(ac_rate)
            * recency_weight(days_ago)
        )
        for topic in topics:
            raw_scores[topic] += score_contribution
    
    # Sigmoid normalize 0->weak, 1->strong
    if not raw_scores:
        return {}
    max_val = max(raw_scores.values()) or 1
    return {
        topic: round(1 / (1 + math.exp(-5 * (score / max_val - 0.5))), 4)
        for topic, score in raw_scores.items()
    }
        


    

