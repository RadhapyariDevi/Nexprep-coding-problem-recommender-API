from fastapi import APIRouter, HTTPException, Query
from config import ALFA_API_BASE
from LEETCODE.models.schemas import (
    RecommendationResponse, MasteryResponse, WeakSpotsResponse,
    DifficultyCalibrationResponse, RecommendRequest, HealthResponse,
    MasteryTopic, WeakSpot
)

from LEETCODE.services.recommender import generate_recommendations
from LEETCODE.services.leetcode_client import LeetCodeClient
from LEETCODE.services.mastery import build_mastery_vector
from LEETCODE.services.calibrator import calibrate_difficulty
import httpx, time
import asyncio

router = APIRouter(tags=["Nexprep"])
client = LeetCodeClient()



#  Health check 
@router.get("/health", response_model=HealthResponse, summary="Health check", tags=["Meta"])
async def health_check():
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(ALFA_API_BASE, timeout=30.0)  # hit root "/" not "/health"
            alfa_ok = r.status_code == 200
    except Exception:
        alfa_ok = False

    return HealthResponse(
        status="ok",
        alfa_api_reachable=alfa_ok,
        version="1.0.0"
    )


# core route : recommend
@router.get(
    "/recommend/{username}",
    response_model=RecommendationResponse,
    summary="Get personalized problem recommendations",
    description="Returns ranked problems targeting the user's weakest topics, calibrated to their difficulty frontier."
)
async def get_recommendations(
    username: str,
    top_k: int = Query(default=10, ge=1, le=30, description="How many problems to return")
):
    try:
        result = await generate_recommendations(username, top_k=top_k)
        return result
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on LeetCode")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# mastery vector route
@router.get(
    "/mastery/{username}",
    response_model = MasteryResponse,
    summary="Get topic mastery breakdown",
    description="Returns the computed mastery score (0.0–1.0) for every topic, with strongest and weakest highlighted."
)
async def get_mastery(username: str):
    try:
        skill_stats, submissions = await asyncio.gather(
            client.get_skill_stats(username),
            client.get_submissions(username, limit=100)
        )
        ac_list = submissions.get("submission", [])
        mastery_vector = build_mastery_vector(skill_stats, ac_list, {}, int(time.time()))


        def level(score: float) -> str:
            if score < 0.35: return "beginner"
            if score < 0.65: return "intermediate"
            return "strong"
        
        topics = [
            MasteryTopic(topic=t, mastery=round(s, 3), level=level(s))
            for t, s in sorted(mastery_vector.items(), key=lambda x: x[1])
        ]

        return MasteryResponse(
            username=username,
            topics=topics,
            strongest=sorted(topics, key=lambda x: x.mastery, reverse=True)[:3],
            weakest=topics[:3]
        )
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# weak spots route
@router.get(
    "/weakspots/{username}",
    response_model=WeakSpotsResponse,
    summary="Get weak topic analysis with suggestions",
    description="Identifies the user's critical weak areas and returns human-readable improvement suggestions."
)
async def get_weakspots(username:str):
    try:
        skill_stats, submissions, solved_stats = await asyncio.gather(
            client.get_skill_stats(username),
            client.get_submissions(username, limit=100),
            client.get_solved_stats(username)
        )

        ac_list = submissions.get("submission", [])
        mastery_vector = build_mastery_vector(skill_stats, ac_list, {}, int(time.time()))
        calibration = calibrate_difficulty(solved_stats)

        weak = sorted(mastery_vector.items(), key=lambda x: x[1])[:6]

        suggestions_map = {
            (0.0, 0.2): "You've barely touched this — start with 3 Easy problems this week",
            (0.2, 0.4): "Foundational gaps here — drill 5 Medium problems before moving on",
            (0.4, 0.6): "Decent base but inconsistent — focus on pattern recognition here",
        }

        def get_suggestion(score: float) -> str:
            for (low, high), msg in suggestions_map.items():
                if low <= score < high:
                    return msg
            return "Reinforce with harder variants"
        
        # Generate insight summary
        zero_mastery = [t for t, s in weak if s < 0.1]
        insight = (
            f"You have zero exposure to: {', '.join(zero_mastery[:3])}" 
            if zero_mastery 
            else f"Your weakest area is '{weak[0][0]}' — that's your highest leverage point right now"
        )
        return WeakSpotsResponse(
            username=username,
            weak_spots=[
                WeakSpot(topic=t, mastery=round(s, 3), suggestion=get_suggestion(s))
                for t, s in weak
            ],
            recommended_difficulty=calibration["recommended_difficulty"],
            insight=insight
        )
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# difficulty calibration route

@router.get(
    "/calibrate/{username}",
    response_model=DifficultyCalibrationResponse,
    summary="Calibrate recommended difficulty level",
    description="Analyzes solve ratios and contest rating to determine where the user's learning frontier is."
)
async def calibrate_user(username: str):
    try:
        solved_stats, contest = await asyncio.gather(
            client.get_solved_stats(username),
            client.get_contest(username)
        )
        contest_rating = contest.get("contestRating")
        calibration = calibrate_difficulty(solved_stats, contest_rating)

        return DifficultyCalibrationResponse(
            username=username,
            calibration=calibration,
            breakdown={
                "easy": solved_stats.get("easySolved", 0),
                "medium": solved_stats.get("mediumSolved", 0),
                "hard": solved_stats.get("hardSolved", 0)
            },
            contest_rating=contest_rating
        )
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


