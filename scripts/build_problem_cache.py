import json
import asyncio
from services.leetcode_client import LeetCodeClient

client = LeetCodeClient()

async def main():
    cache = {}
    skip = 0
    limit = 100

    while True:
        result = await client.get_problems(limit=limit, skip=skip)

        problems = result["problemsetQuestionList"]

        if not problems:
            break

        for p in problems:
            cache[p["titleSlug"]] = {
                "difficulty": p["difficulty"],
                "acRate": p["acRate"],
                "topicTags": [t["slug"] for t in p["topicTags"]]
            }

        print(f"Fetched {len(cache)}")

        skip += limit

    with open("problem_cache.json", "w", encoding="utf-8") as f:
        json.dump(cache, f)

    print(f"Saved {len(cache)} problems")

asyncio.run(main())