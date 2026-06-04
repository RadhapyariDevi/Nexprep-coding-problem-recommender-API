from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class RecommendRequest(BaseModel):
    top_k: int = Field(
        default=10,
        ge=1,
        le=30,
        description="Number of problems to recommend"
    )


class CalibrationResult(BaseModel):
    recommended_difficulty: str
    confidence: float
    medium_to_easy_ratio: float
    hard_to_medium_ratio: float


class RecommendedProblem(BaseModel):
    title: str
    titleSlug: str
    difficulty: str
    acRate: float
    url: str
    topicTags: List[str]
    why_recommended: str
    your_mastery_in_topic: Dict[str, float]


class MasteryTopic(BaseModel):
    topic: str
    mastery: float                 
    level: str 


class WeakSpot(BaseModel):
    topic: str
    mastery: float
    suggestion: str


# Response models
class RecommendationResponse(BaseModel):
    username: str
    calibration: CalibrationResult
    recommendations: List[RecommendedProblem]
    mastery_snapshot: Dict[str, float]

class MasteryResponse(BaseModel):
    username: str
    topics: List[MasteryTopic]
    strongest: List[MasteryTopic]   # top 3
    weakest: List[MasteryTopic]     # bottom 3

class WeakSpotsResponse(BaseModel):
    username: str
    weak_spots: List[WeakSpot]
    recommended_difficulty: str
    insight: str                   

class DifficultyCalibrationResponse(BaseModel):
    username: str
    calibration: CalibrationResult
    breakdown: Dict[str, int]       # { "easy": 120, "medium": 45, "hard": 8 }
    contest_rating: Optional[float]

class HealthResponse(BaseModel):
    status: str
    alfa_api_reachable: bool
    version: str