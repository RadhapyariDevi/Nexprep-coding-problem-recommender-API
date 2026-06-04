import asyncio
from services.leetcode_client import LeetCodeClient
c = LeetCodeClient()
print(asyncio.run(c.get_problems_by_tag("graph", difficulty="medium", limit=5)))



from services.mastery import build_mastery_vector
fake_skill = {"fundamental": [{"tagSlug": "array", "problemsSolved": 100}], "intermediate": [], "advanced": []}
print(build_mastery_vector(fake_skill, [], {}, 0))