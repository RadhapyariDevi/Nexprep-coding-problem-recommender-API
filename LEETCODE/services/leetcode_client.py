import httpx
from config import ALFA_API_BASE

class LeetCodeClient:
    def __init__(self):
        self.base = ALFA_API_BASE
    

    #fetch user profile data from alfa api
    async def get_profile(self, username:str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base}/{username}/profile", timeout=15)
            r.raise_for_status()
            return r.json()
        
    #fetch user skill stats from alfa api
    async def get_skill_stats(self, username: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base}/{username}/skill", timeout=15)
            r.raise_for_status()
            return r.json()
    
    #fetch user submissions from alfa api
    async def get_submissions(self, username: str, limit: int = 50) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base}/{username}/acSubmission",
                params={"limit": limit},
                timeout=15
            )
            r.raise_for_status()
            return r.json()
        
    #fetch problems by tag
    async def get_problems_by_tag(self, tag: str, difficulty: str = None, limit: int = 10) -> dict:
        params = {"tags": tag, "limit": limit}
        if difficulty:
            params["difficulty"] = difficulty.upper()
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base}/problems", params=params, timeout=15)
            r.raise_for_status()
            return r.json()
    
    #fetch user solved stats
    async def get_solved_stats(self, username: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base}/{username}/solved", timeout=15)
            r.raise_for_status()
            return r.json()
        
    #fetch user contest data
    async def get_contest(self, username: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base}/{username}/contest", timeout=15)
            r.raise_for_status()
            return r.json()
        
    #fetch problem details by slug
    async def get_problem_details(self, slug: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base}/select?titleSlug={slug}", timeout=15)
            r.raise_for_status()
            return r.json()
        
    async def get_problems(self, limit=100, skip=0):
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base}/problems?limit={limit}&skip={skip}"
            )
            r.raise_for_status()
            return r.json()
