import asyncio
import time
from collections import Counter

from LEETCODE.services.leetcode_client import LeetCodeClient
from LEETCODE.services.mastery import build_mastery_vector
from LEETCODE.services.calibrator import calibrate_difficulty
from LEETCODE.services.scorer import rank_problems
from LEETCODE.services.problem_cache import get_problem, get_problems_by_tag_local

client = LeetCodeClient()

async def generate_recommendations(username: str, top_k: int = 10) -> dict:

    # fetch all required data concurrently
    
    profile, skill_stats, submissions, solved_stats, contest = await asyncio.gather(
        client.get_profile(username),
        client.get_skill_stats(username),
        client.get_submissions(username, limit=100),
        client.get_solved_stats(username),
        client.get_contest(username),
    )

    ac_list = submissions.get("submission", [])
    contest_rating = contest.get("contestRating", None)

    already_solved = {s["titleSlug"] for s in ac_list}

    attempt_counts = Counter(s["titleSlug"] for s in ac_list)

    problem_details = {}
    for s in ac_list:
        slug = s.get("titleSlug", "")
        if slug:
            details = get_problem(slug)

            if details:
                problem_details[slug] = details


    # Build mastery vector 
    mastery_vector = build_mastery_vector(
        skill_stats, ac_list, problem_details, int(time.time())
    )


    # Calibrate target difficulty 
    calibration = calibrate_difficulty(solved_stats, contest_rating)
    target_difficulty = calibration["recommended_difficulty"]


    #Find weakest topics to fetch candidates from
    weak_topics = sorted(mastery_vector.items(), key=lambda x: x[1])[:5]


    # Fetch candidate problems for weak topics 
    candidate_fetch = [
        get_problems_by_tag_local(
            tag,
            target_difficulty,
            limit=20
        )
        for tag, _ in weak_topics
    ]
    candidates = []
    for result in candidate_fetch:
        candidates.extend(result)

    
    
    # Deduplicate

    seen = set()
    unique_candidates = []
    for p in candidates:
        slug = p.get("titleSlug")
        if slug and slug not in seen:
            seen.add(slug)
            unique_candidates.append(p)


    # Score & rank 


    ranked = rank_problems(
        unique_candidates, mastery_vector,
        target_difficulty, already_solved, attempt_counts, top_k
    )


    #  recommendation
    for problem in ranked:
        # extract slug from each topicTag dict
        problem["url"] = f"https://leetcode.com/problems/{problem.get('titleSlug')}/"
    
        topic_slugs = [
            t["slug"] if isinstance(t, dict) else t
            for t in problem.get("topicTags", [])
        ]
        
        weak_match = [
            slug for slug in topic_slugs
            if mastery_vector.get(slug, 0) < 0.4
        ]
        
        problem["why_recommended"] = (
            f"Targets your weak areas: {', '.join(weak_match[:2])}"
            if weak_match else "Balances your skill profile"
        )
        problem["your_mastery_in_topic"] = {
            slug: round(mastery_vector.get(slug, 0.0), 3)
            for slug in topic_slugs
        }
        problem["topicTags"] = topic_slugs  # flatten to strings for clean response
        problem.pop("_score", None)

    return {
        "username": username,
        "mastery_snapshot": {k: round(v, 3) for k, v in sorted(mastery_vector.items(), key=lambda x: x[1])},
        "calibration": calibration,
        "recommendations": ranked
    }



