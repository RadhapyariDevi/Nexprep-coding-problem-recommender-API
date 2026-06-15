from LEETCODE.services.problem_vectorizer import get_tag_slug, vectorize_problem, vectorize_user_weakness, cosine_similarity
from typing import List, Dict
import math


def score_problem(
    problem: dict,
    user_weakness_vec,
    mastery_vector: dict,
    already_solved_slugs: set,
    submission_attempt_counts: dict   # slug → how many times attempted before AC
) -> float:
    """
    Final score = base_similarity
                * novelty_bonus
                * struggle_penalty_avoidance
                * unseen_bonus
    """
    slug = problem.get("titleSlug", "")
    if slug in already_solved_slugs:
        return -1.0
    
    # Vectorize problem and compute base similarity
    prob_vec = vectorize_problem(problem)
    base_sim = cosine_similarity(prob_vec, user_weakness_vec)


    # Novelty bonus - Recommend topics the user hasn't mastered yet.
    topic_scores = []
    for tag in problem.get("topicTags", []):
        mastery = mastery_vector.get(get_tag_slug(tag), 0.0) 
        topic_scores.append(mastery)
    avg_mastery = sum(topic_scores) / len(topic_scores) if topic_scores else 0.5
    novelty_bonus = 1.0 + (0.5 * (1.0 - avg_mastery)) 


    attempts = submission_attempt_counts.get(slug, 0)
    struggle_multiplier = 1.0
    if attempts > 4:
        struggle_multiplier = 0.7  # they've already fought this, skip for now


    #  Acceptance rate zone - don't recommend problems that are too easy or impossible
    ac_rate = problem.get("acRate", 50.0)
    if ac_rate > 75:
        ac_zone = 0.6   # too easy, low value
    elif 30 <= ac_rate <= 70:
        ac_zone = 1.0   # sweet spot
    else:
        ac_zone = 0.85  # very hard

    final_score = base_sim * novelty_bonus * struggle_multiplier * ac_zone
    return final_score




def rank_problems(
    candidate_problems: List[dict],
    mastery_vector: dict,
    target_difficulty: str,
    already_solved: set,
    attempt_counts: dict,
    top_k: int = 10
) -> List[dict]:
    """
    Scores all candidates and returns top_k sorted by final_score.
    """
    user_vec = vectorize_user_weakness(mastery_vector, target_difficulty)

    scored = []
    for problem in candidate_problems:
        score = score_problem(
            problem, user_vec, mastery_vector,
            already_solved, attempt_counts
        )
        if score > 0:
            scored.append({**problem, "_score": round(score, 4)})

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return scored[:top_k]

