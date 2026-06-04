import asyncio
from services.leetcode_client import LeetCodeClient
c = LeetCodeClient()
# print(asyncio.run(c.get_problem_details("find-the-duplicate-number")))
print(asyncio.run(c.get_problems(limit=1)))


# from services.mastery import build_mastery_vector
# fake_skill = {"fundamental": [{"tagSlug": "array", "problemsSolved": 100}], "intermediate": [], "advanced": []}
# print(build_mastery_vector(fake_skill, [], {}, 0))