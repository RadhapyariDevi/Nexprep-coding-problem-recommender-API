import asyncio
from services.leetcode_client import LeetCodeClient
c = LeetCodeClient()
print(asyncio.run(c.get_skill_stats("username")))