import json

with open("problem_cache.json", "r", encoding="utf-8") as f:
    PROBLEM_CACHE = json.load(f)


def get_problem(slug: str):
    return PROBLEM_CACHE.get(slug)




def get_problems_by_tag_local(tag, difficulty, limit=20):
    results = []

    for problem in PROBLEM_CACHE.values():

        if (
            tag in problem.get("topicTags", [])
            and problem.get("difficulty", "").upper() == difficulty.upper()
        ):
            results.append(problem)

    return results[:limit]