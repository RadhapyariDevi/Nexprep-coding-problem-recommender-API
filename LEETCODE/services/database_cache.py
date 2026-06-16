
from cf.database import leetcode_collection

print("[cache] Loading problems from MongoDB into memory...")
_cache = {doc["slug"]: doc for doc in leetcode_collection.find({}, {"_id": 0})}
print(f"[cache] Loaded {len(_cache)} problems into memory")


def get_problem(slug: str):
    return _cache.get(slug)


def get_problems_by_tag_local(tag: str, difficulty: str, limit: int = 20):
    difficulty = difficulty.capitalize()
    results = []
    for problem in _cache.values():
        if tag in problem.get("topicTags", []) and problem.get("difficulty") == difficulty:
            results.append(problem)
            if len(results) >= limit:
                break
    return results