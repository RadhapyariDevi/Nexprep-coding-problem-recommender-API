import asyncio
from LEETCODE.services.leetcode_client import LeetCodeClient
from cf.database import leetcode_collection
from pymongo import UpdateOne

client = LeetCodeClient()

async def main():
    skip = 0
    limit = 100
    total_synced = 0

    while True:
        result = await client.get_problems(limit=limit, skip=skip)
        problems = result.get("problemsetQuestionList", [])

        if not problems:
            break

        operations = []
        for p in problems:
            doc = {
                "slug": p["titleSlug"],
                "title": p["title"],
                "titleSlug": p["titleSlug"],
                "difficulty": p["difficulty"],
                "acRate": p["acRate"],
                "topicTags": [t["slug"] for t in p["topicTags"]]
            }
            
            operations.append(
                UpdateOne({"slug": doc["slug"]}, {"$set": doc}, upsert=True)
            )

        if operations:
            leetcode_collection.bulk_write(operations)
            total_synced += len(operations)

        print(f"Fetched and synced {total_synced} problems...")
        skip += limit

    print(f"Successfully stored {total_synced} LeetCode problems directly to MongoDB Atlas!")

asyncio.run(main())