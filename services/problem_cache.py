import json

with open("problem_cache.json", "r", encoding="utf-8") as f:
    PROBLEM_CACHE = json.load(f)

def get_problem(slug: str):
    return PROBLEM_CACHE.get(slug)