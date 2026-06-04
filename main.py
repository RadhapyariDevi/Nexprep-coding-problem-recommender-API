import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.recommend import router
from config import ALFA_API_BASE

app = FastAPI(
    title="Nexprep - LeetCode Problem Recommender",
    description="Smart LeetCode recommendations driven by your mastery vector — not random grinding",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")